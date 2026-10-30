"""Export a tiny deterministic smoke model. This is NOT a trained classifier."""
from pathlib import Path
import torch
from executorch.exir import to_edge
class AddOne(torch.nn.Module):
    def forward(self,x): return x+1
root=Path(__file__).resolve().parents[1]
sample=torch.tensor([[1.,2.,3.,4.]])
program=to_edge(torch.export.export(AddOne().eval(),(sample,))).to_executorch()
(root/'models/add_one.pte').write_bytes(program.buffer)
print('Exported models/add_one.pte; input [[1,2,3,4]], shape [1,4], expected [[2,3,4,5]]')
