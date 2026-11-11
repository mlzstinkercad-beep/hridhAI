from typing import Dict, Iterator, Tuple
import torch
from torchvision import datasets


class InMemoryTensorDataset:
    """
    High-speed in-RAM dataset container.
    Pre-allocates contiguous float32 image tensors and int64 label tensors in RAM
    to eliminate DataLoader multiprocessing & PIL serialization bottlenecks.
    """

    def __init__(self, images: torch.Tensor, labels: torch.Tensor):
        assert images.shape[0] == labels.shape[0], "Image and label counts must match."
        self.images = images.contiguous()
        self.labels = labels.contiguous()
        self.num_samples = images.shape[0]

    def __len__(self) -> int:
        return self.num_samples

    def iter_batches(
        self,
        batch_size: int,
        shuffle: bool = False,
        device: torch.device = torch.device("cpu"),
    ) -> Iterator[Tuple[torch.Tensor, torch.Tensor]]:
        """Yield contiguous slices directly from RAM/VRAM."""
        if shuffle:
            perm = torch.randperm(self.num_samples)
        else:
            perm = torch.arange(self.num_samples)

        for start_idx in range(0, self.num_samples, batch_size):
            batch_idx = perm[start_idx : start_idx + batch_size]
            yield (
                self.images[batch_idx].to(device, non_blocking=True),
                self.labels[batch_idx].to(device, non_blocking=True),
            )

    def subset(self, count: int, seed: int = 42) -> "InMemoryTensorDataset":
        """Return a deterministic subset of samples."""
        g = torch.Generator().manual_seed(seed)
        perm = torch.randperm(self.num_samples, generator=g)[:count]
        return InMemoryTensorDataset(self.images[perm].clone(), self.labels[perm].clone())


class MNISTDataManager:
    """
    Manages separated train, scanner-reference (val), and held-out test splits.
    All pixel intensities are normalized to [0.0, 1.0] in shape (N, 1, 28, 28).
    """

    def __init__(self, data_dir: str = "./data", seed: int = 42):
        self.data_dir = data_dir
        self.seed = seed

    def load_splits(self) -> Dict[str, InMemoryTensorDataset]:
        raw_train = datasets.MNIST(root=self.data_dir, train=True, download=True)
        raw_test = datasets.MNIST(root=self.data_dir, train=False, download=True)

        # Convert uint8 (N, 28, 28) -> float32 (N, 1, 28, 28) in [0, 1] directly in RAM
        train_x = raw_train.data.unsqueeze(1).to(torch.float32).div_(255.0)
        train_y = raw_train.targets.to(torch.long)

        test_x = raw_test.data.unsqueeze(1).to(torch.float32).div_(255.0)
        test_y = raw_test.targets.to(torch.long)

        # Split 60,000 train into 55,000 training and 5,000 clean scanner reference
        g = torch.Generator().manual_seed(self.seed)
        perm = torch.randperm(train_x.shape[0], generator=g)
        train_idx, val_idx = perm[:55000], perm[55000:]

        return {
            "train": InMemoryTensorDataset(train_x[train_idx], train_y[train_idx]),
            "scanner_ref": InMemoryTensorDataset(train_x[val_idx], train_y[val_idx]),
            "test": InMemoryTensorDataset(test_x, test_y),
        }