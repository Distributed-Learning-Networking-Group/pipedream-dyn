import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn as nn
import torch.optim as optim
from torch.nn.parallel import DistributedDataParallel as DDP
import os

def example(rank, world_size):
    # create default process group
    dist.init_process_group("gloo", rank=rank, world_size=world_size)
    # create local model
    model = nn.Linear(10, 10).to(rank)
    # construct DDP model
    ddp_model = DDP(model, device_ids=[rank])
    # define loss function and optimizer
    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(ddp_model.parameters(), lr=0.001)

    # forward pass
    for i in range(100):
        print(i)
        if rank==0:
            outputs = ddp_model(torch.randn(1, 10).to(rank))
            labels = torch.randn(1, 10).to(rank)
        if rank==1:
            outputs = ddp_model(torch.randn(2, 10).to(rank))
            labels = torch.randn(2, 10).to(rank)
        # backward pass
        loss_fn(outputs, labels).backward()
        # update parameters
        optimizer.step()
        print(outputs)
def main():
    world_size = 2
    example(0,2)

if __name__=="__main__":
    # Environment variables which need to be
    # set when using c10d's default "env"
    # initialization mode.
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29500"
    main()