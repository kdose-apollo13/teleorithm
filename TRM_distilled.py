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
    def __init__(self, in_dim=2, enc_dim=8, out_dim=1):
        super().__init__()
        self.enc_dim = enc_dim

        self.x_enc = Linear(in_dim, enc_dim)
        self.y_enc = Linear(out_dim, enc_dim)
        self.y_dec = Linear(enc_dim, out_dim)
        self.net = Linear(3 * enc_dim, enc_dim)

        self.q_head = Linear(enc_dim, 1)
    
    def forward(self, xs, T, n):
        batch_size, _ = xs.shape

        xs_e = self.x_enc(xs)
        ys = torch.randn(batch_size, 1)
        ys_e = self.y_enc(ys)
        zs = torch.randn(batch_size, self.enc_dim)

        null = torch.zeros_like(xs_e)

        def dream(xs, ys, zs):
            """RUNS NET"""
            o = torch.cat([xs, ys, zs], dim=-1)
            return torch.tanh(self.net(o))

        with torch.no_grad():
            for _ in range(T-1):
                for _ in range(n):
                    zs = dream(xs_e, ys_e, zs)
                ys_e = dream(null, ys_e, zs)
                
        for _ in range(n):
            zs = dream(xs_e, ys_e, zs)
        ys_e = dream(null, ys_e, zs)

        y_hat = self.y_dec(ys_e)
        q_hat = torch.sigmoid(self.q_head(ys_e))

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
                ce = F.binary_cross_entropy_with_logits(y_hat, ys)

                # quality gets detached, no gradient flow
                quality = (F.sigmoid(y_hat) > 0.5) == ys
                act = F.binary_cross_entropy(q_hat, quality.float())

                loss = ce + 0.5 * act
                loss.backward()
                opt.step()
                opt.zero_grad()
                total_loss += loss.item()

    model.eval()
    with torch.no_grad():
        y_hat, _ = model(x, T, n)
        blunted = F.sigmoid(y_hat) > 0.5
        acc = (blunted == y).float().mean().item()

    return acc


if __name__ == '__main__':
    from random import randint
    from statistics import mean

    N_sup = 3
    T = 1
    n = 3
    lr = 0.02
    epochs = 11

    # runtime on cpu ~ 1s x runs (eg) 20 runs -> 20 seconds
    runs = 10
    seeds = [randint(1, 1_000_000) for _ in range(runs)]

    accs = []
    for s in seeds:
        a = run(N_sup, T, n, lr, epochs, s)
        accs.append(a)

    print(f'mean accuracy: {mean(accs):.0%}')

