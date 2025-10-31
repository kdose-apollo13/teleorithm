# gemini
import torch
from torch.optim import AdamW
from torch.nn import (
    Embedding, Linear, Module, LSTM, 
    CrossEntropyLoss, functional as F
)
from torch.utils.data import Dataset, DataLoader, TensorDataset
import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import warnings

# --- 1. Data Loading and Preparation ---

# Create a dummy mobydick.txt if it doesn't exist
try:
    with open('mobydick.txt', 'rt') as r:
        text = r.read()
except FileNotFoundError:
    print("Warning: 'mobydick.txt' not found. Using dummy text.")
    text = """
    Call me Ishmael. Some years ago—never mind how long precisely—having
    little or no money in my purse, and nothing particular to interest me on
    shore, I thought I would sail about a little and see the watery part of
    the world. It is a way I have of driving off the spleen and regulating
    the circulation. Whenever I find myself growing grim about the mouth;
    whenever it is a damp, drizzly November in my soul; whenever I find
    myself involuntarily pausing before coffin warehouses, and bringing up
    the rear of every funeral I meet; and especially whenever my hypos
    get such an upper hand of me, that it requires a strong moral
    principle to prevent me from deliberately stepping into the street,
    and methodically knocking people’s hats off—then, I account it high
    time to get to sea as soon as I can. This is my substitute for
    pistol and ball. With a philosophical flourish Cato throws himself
    upon his sword; I quietly take to the ship. There is nothing
    surprising in this. If they but knew it, almost all men in their
    degree, some time or other, cherish very nearly the same feelings
    towards the ocean with me.
    
    ... (Text truncated for this example) ...
    """

text = text[:3_000] # Use a 3000-char snippet

vocab = sorted(list(set(text)))
vocab_size = len(vocab)

char_to_ix = {ch: i for i, ch in enumerate(vocab)}
ix_to_char = {i: ch for i, ch in enumerate(vocab)}

data = [char_to_ix[ch] for ch in text]
data_tensor = torch.tensor(data, dtype=torch.long)

def get_batches(split, batch_size=32, block_size=8):
    """Samples random batches of x (inputs) and y (targets)"""
    ix = torch.randint(len(split) - block_size, (batch_size,))
    x = torch.stack([split[i:i+block_size] for i in ix])
    y = torch.stack([split[i+1:i+block_size+1] for i in ix])
    return x, y

# --- 2. Model Definition ---

class CharLM(Module):
    def __init__(self, vocab_size, embed_dim=32, hidden_dim=64):
        super().__init__()
        self.embed = Embedding(vocab_size, embed_dim)
        self.lstm = LSTM(embed_dim, hidden_dim, batch_first=True)
        self.out = Linear(hidden_dim, vocab_size)
        self.hidden_dim = hidden_dim
    
    def forward(self, x, capture_latent=False):
        embeds = self.embed(x) 
        lstm_out, (hidden, cell) = self.lstm(embeds)
        logits = self.out(lstm_out)
        
        if capture_latent:
            # Detach to prevent gradients from flowing back during probing
            return logits, lstm_out.detach()
        return logits

# --- 3. LatentProbe Class (Suggestions 1, 2, 3, 4, 5) ---

class LatentProbe:
    """A self-contained class for analyzing a model's latent space."""
    
    def __init__(self, model, text_data_tensor, ix_to_char, char_to_ix):
        print("Initializing LatentProbe: Capturing full latent trajectory...")
        self.model = model
        self.data = text_data_tensor
        self.ix_to_char = ix_to_char
        self.char_to_ix = char_to_ix
        
        # Capture full-sequence latents and corresponding inputs
        self.latents, self.inputs = self._capture_full_trajectory()
        self.embeds = model.embed.weight.data.cpu().numpy()
        self.vocab_size = model.embed.num_embeddings
        print(f"Captured latents shape: {self.latents.shape}")

    @torch.no_grad()
    def _capture_full_trajectory(self):
        """Runs the model over the entire dataset to get all hidden states."""
        self.model.eval()
        # Full input sequence (e.g., chars 0...N-1)
        full_input = self.data[:-1].unsqueeze(0) # (1, N-1)
        _, latents = self.model(full_input, capture_latent=True)
        
        # Squeeze batch dim and move to CPU
        latents_np = latents.squeeze(0).cpu().numpy() # (N-1, hidden_dim)
        inputs_np = full_input.squeeze(0).cpu().numpy() # (N-1)
        return latents_np, inputs_np

    def get_effective_dim(self):
        """(Original Metric) Calculates effective dimensionality via SVD."""
        U, S, Vt = np.linalg.svd(self.latents, full_matrices=False)
        # Rule-of-thumb: count singular values > 1% of the max
        eff_dim = np.sum(S > 1e-2 * S[0])
        return eff_dim, self.latents.shape[1]

    def get_consecutive_similarity(self):
        """(Original Metric) Measures average cosine sim between h(t) and h(t+1)."""
        sims = [cosine_similarity([self.latents[i]], [self.latents[i+1]])[0,0] 
                for i in range(len(self.latents)-1)]
        return np.mean(sims)

    def get_pca_projection(self, n_components=2):
        """Projects latents into 2D or 3D for visualization."""
        pca = PCA(n_components=n_components)
        lat_proj = pca.fit_transform(self.latents)
        explained_var = pca.explained_variance_ratio_.sum()
        return lat_proj, explained_var

    def plot_trajectory(self):
        """(Suggestion 1) Plots the 2D PCA of the trajectory, colored by char type."""
        lat2d, explained_var = self.get_pca_projection(n_components=2)
        
        # Map chars to colors
        char_types = {}
        for v in 'aeiouAEIOU': char_types[v] = 'red'
        for p in ' .,\n;:-?!\'': char_types[p] = 'gray'
        
        # Get colors, default to 'blue' for other consonants
        chars = [self.ix_to_char[idx] for idx in self.inputs]
        colors = [char_types.get(ch, 'blue') for ch in chars]

        plt.figure(figsize=(12, 7))
        plt.scatter(lat2d[:,0], lat2d[:,1], c=colors, s=5, alpha=0.6)
        plt.plot(lat2d[:,0], lat2d[:,1], 'k-', linewidth=0.5, alpha=0.3)
        plt.title(f"Latent Trajectory (PCA: {explained_var:.2f} Var Explained)")
        plt.xlabel("PC1")
        plt.ylabel("PC2")
        
        # Create a custom legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', label='Vowel'),
            Patch(facecolor='blue', label='Consonant'),
            Patch(facecolor='gray', label='Space/Punct.')
        ]
        plt.legend(handles=legend_elements)
        
        # Annotate start/end
        plt.scatter([lat2d[0,0], lat2d[-1,0]], [lat2d[0,1], lat2d[-1,1]], c=['green','black'], s=100, zorder=5)
        plt.text(lat2d[0,0], lat2d[0,1], "START", fontsize=12)
        plt.text(lat2d[-1,0], lat2d[-1,1], "END", fontsize=12)
        plt.show()

    def plot_similarity_heatmap(self, max_steps=200):
        """(Suggestion 3) Plots the cosine similarity matrix of hidden states."""
        print(f"Plotting similarity heatmap for first {max_steps} states...")
        if len(self.latents) < max_steps:
            max_steps = len(self.latents)
            warnings.warn(f"Dataset smaller than max_steps. Using {max_steps} steps.")

        sim_matrix = cosine_similarity(self.latents[:max_steps, :])
        
        plt.figure(figsize=(9, 8))
        plt.imshow(sim_matrix, cmap='viridis', origin='lower')
        plt.title(f"Latent State Similarity Heatmap (First {max_steps} Chars)")
        plt.xlabel("Time Step (t)")
        plt.ylabel("Time Step (t)")
        plt.colorbar(label="Cosine Similarity")
        plt.show()

    def run_information_probe(self, probe_steps=100, lr=1e-3):
        """(Suggestion 2) Trains a linear probe to predict x(t) from h(t)."""
        print("Running information probe (h_t -> x_t)...")
        # Probe is a simple linear classifier
        probe = Linear(self.model.hidden_dim, self.vocab_size)
        probe_opt = AdamW(probe.parameters(), lr=lr)
        probe_loss_fn = CrossEntropyLoss()
        
        # Convert latents/inputs to Tensors for training the probe
        probe_latents = torch.from_numpy(self.latents)
        probe_inputs = torch.from_numpy(self.inputs)

        for step in range(probe_steps):
            probe_logits = probe(probe_latents) # Predict x_t from h_t
            loss = probe_loss_fn(probe_logits, probe_inputs)
            probe_opt.zero_grad()
            loss.backward()
            probe_opt.step()
            if step % 50 == 0:
                print(f"  Probe step {step}, Loss: {loss.item():.4f}")

        # Check final probe accuracy
        with torch.no_grad():
            probe_logits = probe(probe_latents)
            probe_acc = (probe_logits.argmax(-1) == probe_inputs).float().mean()
        print(f"Probe accuracy (h_t -> x_t): {probe_acc.item():.3f}")
        return probe_acc.item()

    @torch.no_grad()
    def get_perturbation_sensitivity(self, noise_level=0.01, batch_size=32, block_size=8):
        """(Suggestion 4) Measures KL Div between original and noisy-latent predictions."""
        self.model.eval()
        
        # Get a representative batch
        xb, yb = get_batches(self.data, batch_size=batch_size, block_size=block_size)
        
        # 1. Original logits
        logits_orig, latents_orig = self.model(xb, capture_latent=True)
        
        # 2. Add noise and re-run *only* the output layer
        noise = torch.randn_like(latents_orig) * noise_level
        latents_noisy = latents_orig + noise
        logits_noisy = self.model.out(latents_noisy) # Re-use original .out layer

        # 3. Measure difference using KL Divergence
        # F.kl_div(input, target) -> input should be log-probs, target should be probs
        log_p = F.log_softmax(logits_orig.view(-1, self.vocab_size), dim=-1)
        q = F.softmax(logits_noisy.view(-1, self.vocab_size), dim=-1)
        
        # Use reduction='batchmean' which divides by batch size (B*T)
        sensitivity = F.kl_div(log_p, q, log_target=False, reduction='batchmean')
        
        return sensitivity.item()

# --- 4. Training ---

model = CharLM(vocab_size)
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

optimizer = AdamW(model.parameters(), lr=2e-3)
loss_fn = CrossEntropyLoss()

def train_epoch(num_steps=300): # Increased steps for better training
    model.train()
    total_loss = 0
    for step in range(num_steps):
        xb, yb = get_batches(data_tensor, block_size=8)
        logits = model(xb)
        loss = loss_fn(logits.view(-1, vocab_size), yb.view(-1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / num_steps

print("--- Starting Model Training ---")
for epoch in range(19): # Increased epochs for better training
    loss = train_epoch()
    if (epoch + 1) % 3 == 0:
        print(f"Epoch {epoch+1}: Avg loss {loss:.4f}")

print("--- Training Complete ---")


# --- 5. Probing and Analysis ---

print("\n--- Initializing Latent Space Analysis ---")
probe = LatentProbe(model, data_tensor, ix_to_char, char_to_ix)

print("\n--- Running Metrics ---")

# Metric: Effective Dimension
eff_dim, max_dim = probe.get_effective_dim()
print(f"Effective Latent Dim: {eff_dim} / {max_dim}")

# Metric: Consecutive Similarity
consec_sim = probe.get_consecutive_similarity()
print(f"Mean Consecutive Similarity: {consec_sim:.3f}")

# Metric: Perturbation Sensitivity
sensitivity = probe.get_perturbation_sensitivity(noise_level=0.02)
print(f"Latent Sensitivity (KL Div): {sensitivity:.6f}")

# Metric: Information Probe
probe_acc = probe.run_information_probe()

print("\n--- Generating Visualizations ---")

# Viz: Latent Similarity Heatmap
probe.plot_similarity_heatmap(max_steps=200)

# Viz: Color-Coded Trajectory
probe.plot_trajectory()

print("--- Analysis Complete ---")

