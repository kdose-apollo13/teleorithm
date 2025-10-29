"""
    distilled TRM  
    -------------
    judge [
        without grad [
            [ x, y, z -> z ] * n
            [    y, z -> y ]
        ] * T-1

        with grad [
            [ x, y, z -> z ] * n
            [    y, z -> y ]
        ]
    ] * N_sup
"""
import torch
from torch.optim import Adam
from torch.nn import Linear, Module, functional as F
from torch.utils.data import TensorDataset, DataLoader


# XOR
x = torch.tensor(
    [[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32
)
y = torch.tensor(
    [[0],    [1],    [1],    [0]   ], dtype=torch.float32
)

x = x.repeat(25, 1)
y = y.repeat(25, 1)

dataset = TensorDataset(x, y)
loader = DataLoader(dataset=dataset, batch_size=16, shuffle=True)


class TRM(Module):
    def __init__(self, d_x=2, d_z=8, d_y=1):
        super().__init__()
        self.x_embed = Linear(d_x, d_z)
        self.y_embed = Linear(d_y, d_z)
        self.y_unbed = Linear(d_z, d_y)
        self.network = Linear(d_z * 3, d_z)
        self.qualeval = Linear(d_z, d_y)
        self.d_y = d_y
        self.d_z = d_z
    
    def forward(self, xs, T, n):
        batch_size, _ = xs.shape

        xs_e = self.x_embed(xs)
        ys = torch.randn(batch_size, self.d_y)
        ys_e = self.y_embed(ys)
        zs = torch.randn(batch_size, self.d_z)

        null = torch.zeros_like(xs_e)
        
        def query(latent, xs, ys, zs):
            w = torch.cat([xs, ys, zs], dim=-1)
            return F.tanh(latent(w))

        with torch.no_grad():
            for _ in range(T-1):
                for _ in range(n):
                    zs = query(self.network, xs_e, ys_e, zs)
                ys_e = query(self.network, null, ys_e, zs)

        for _ in range(n):
            zs = query(self.network, xs_e, ys_e, zs)
        ys_e = query(self.network, null, ys_e, zs)

        y_hat = F.sigmoid(self.y_unbed(ys_e))
        q_hat = F.sigmoid(self.qualeval(ys_e))

        return y_hat, q_hat


def run(N_sup, T, n, lr, epochs, seed):

    torch.manual_seed(seed)
    model = TRM()
    opt = Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for xs, ys in loader:
            for N in range(N_sup):
                y_hat, q_hat = model(xs, T, n)
                ce = F.binary_cross_entropy(y_hat, ys)
                quality = ((y_hat > 0.5) == ys).float()  # detaches
                act = F.binary_cross_entropy(q_hat, quality)
                loss = ce + 0.5 * act
                loss.backward()
                opt.step()
                opt.zero_grad()
                total_loss += loss.item()

        # if epoch % 2 == 0:
        #     print(f'loss: {total_loss:.4f}')

    model.eval()
    with torch.no_grad():
        y_hat, _ = model(x, T, n)
        blunted = y_hat > 0.5
        acc = (blunted == y).float().mean().item()

    return acc


if __name__ == '__main__':
    from random import randint
    from statistics import mean

    N_sup = 3
    T = 2
    n = 3
    lr = 0.02
    epochs = 11

    # runtime on cpu ~ 1s x runs (eg) 20 runs -> 20 seconds
    runs = 0
    seeds = [randint(1, 1_000_000) for _ in range(runs)]

    accs = []
    for s in [23] + seeds:
        a = run(N_sup, T, n, lr, epochs, s)
        accs.append(a)

    print(f'mean accuracy: {mean(accs):.0%}')

