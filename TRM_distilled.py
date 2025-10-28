"""
    distilled TRM
    -------------
    judge [
        without grad [
            shape [ x, y, z -> z ] * n
            guess [    y, z -> y ]
        ] * T-1

        with grad [
            shape [ x, y, z -> z ] * n
            guess [    y, z -> y ]
        ]
    ] * N_sup

    shape (z) and guess (y) condensed into 'net'
"""
import torch
from torch.optim import Adam
from torch.nn import Linear, Module, functional as F
from torch.utils.data import TensorDataset, DataLoader


torch.manual_seed(23)

# -----------------
# definition of XOR
# -----------------
x = torch.tensor(
    [[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32
)
y = torch.tensor(
    [[0],    [1],    [1],    [0]   ], dtype=torch.float32
)

x = x.repeat(25, 1)
y = y.repeat(25, 1)

dataset = TensorDataset(x, y)
loader = DataLoader(dataset=dataset, batch_size=10, shuffle=True)


class TRM(Module):
    def __init__(self, in_dim=2, enc_dim=4, out_dim=1):
        super().__init__()

        self.x_enc = Linear(in_dim, enc_dim)
        self.y_enc = Linear(out_dim, enc_dim)
        self.y_dec = Linear(enc_dim, out_dim)
        self.net = Linear(3 * enc_dim, enc_dim)
        self.q_head = Linear(enc_dim, 1)
    
    def forward(self, xs, T, n):
        batch_size, _ = xs.shape
        xs_e = self.x_enc(xs)
        
        ys = torch.zeros(batch_size, 1)
        ys_e = self.y_enc(ys)

        zs = torch.zeros(batch_size, 4)
        h = torch.cat([xs_e, ys_e, zs], dim=-1)

        with torch.no_grad():
            for _ in range(T-1):
                for _ in range(n):
                    zs = torch.tanh(self.net(
                            torch.cat([xs_e, ys_e, zs], dim=-1)
                    ))
                ys_e = torch.tanh(self.net(
                        torch.cat([torch.zeros_like(xs_e), ys_e, zs], dim=-1)
                ))
                
        # once more with backprop
        for _ in range(n):
            zs = torch.tanh(self.net(
                    torch.cat([xs_e, ys_e, zs], dim=-1)
            ))
        ys_e = torch.tanh(self.net(
                torch.cat([torch.zeros_like(xs_e), ys_e, zs], dim=-1)
        ))

        y_hat = self.y_dec(ys_e)
        q_hat = torch.sigmoid(self.q_head(ys_e))

        return y_hat, q_hat
            

model = TRM()
opt = Adam(model.parameters(), lr=0.01)

N_sup = 2
T = 2
n = 2

model.train()
for epoch in range(60):
    total_loss = 0

    for xs, ys in loader:
        for N in range(N_sup):
            # 
            y_hat, q_hat = model(xs, T, n)
            # 
            ce = F.binary_cross_entropy_with_logits(y_hat, ys)
            quality = (F.sigmoid(y_hat) > 0.5) == ys
            act = F.binary_cross_entropy(q_hat, quality.float())
            loss = ce + 0.5 * act
            #
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item()

    if epoch % 5 == 0:
        print(f'epoch {epoch}, avg loss: {total_loss / len(loader):.4f}')


model.eval()
with torch.no_grad():
    y_hat, _ = model(x, T, n)
    blunted = F.sigmoid(y_hat) > 0.5
    print(blunted[:10].to(torch.int8).flatten())
    acc = (blunted == y).float().mean().item()
    print(f'accuracy: {acc:.2%}')

