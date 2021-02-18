import numpy as np
import torch
from unet import UNet3D

with torch.no_grad():
    state = torch.load('/home/pablo/.plantseg_models/initialPoint/best_checkpoint.pytorch')

    net = UNet3D(in_channels=1,
                 out_channels=1,
                 f_maps=[32, 64, 128, 256],
                 testing=True)

    net.load_state_dict(state)

    # load and normalize the input
    im = np.load('test_input.npz')
    im = im['arr_0'].astype('float32')
    im -= im.mean()
    im /= im.std()

    # forward pass
    inp = torch.from_numpy(im)
    out = net(inp)
    learn = Learner(dls, # dataloader
                flower_model,
                metrics=[accuracy],
                opt_func= SGD,
                loss_func=nn.CrossEntropyLoss())
    out = out.cpu().numpy()
