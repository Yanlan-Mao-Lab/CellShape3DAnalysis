import numpy as np
import torch
from unet import UNet3D
import h5py

#From https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
def train_model(model, criterion, optimizer, scheduler, num_epochs=25):
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model


# Data augmentation and normalization for training
# Just normalization for validation
transformer_config = {
    'raw': [
        {'name': 'Standardize'},
        {'name': 'RandomFlip'},
        {'name': 'RandomRotate90'},
        {'name': 'RandomRotate', 'axes': [[2, 1]], 'angle_spectrum': 15, 'mode':'reflect'},
        {'name': 'ElasticDeformation', 'spline_order': 3},
        {'name': 'RandomContrast'},
        {'name': 'AdditiveGaussianNoise'},
        {'name': 'AdditivePoissonNoise'},
        {'name': 'ToTensor', 'expand_dims': True}
    ],
    'label': [
        {'name': 'RandomFlip'},
        {'name': 'RandomRotate90'},
        {'name': 'RandomRotate', 'axes': [[2, 1]], 'angle_spectrum': 15, 'mode':'reflect'},
        {'name': 'ElasticDeformation', 'spline_order': 0},
        {'name': 'ToTensor', 'expand_dims': True}
    ]
}



with torch.no_grad():
	state = torch.load('PreTrainedModels/unet3d-arabidopsis-ovules-confocal-ds2x.pytorch')

	net = UNet3D(in_channels=1,
		out_channels=1,
		f_maps=[32, 64, 128, 256],
		testing=True)

	net.load_state_dict(state)

    # load and normalize the input
    inputDir = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/HDF5/RobTetley/';
    nameFile = 'Part2_Decon_c1_t1_predictions_best.h5'
    with h5py.File(inputDir + nameFile) as trainingInput:
    	min_value, max_value, mean, std = calculate_stats(trainingInput)
    	transformer = transforms.get_transformer(transformer_config, min_value=min_value, max_value=max_value,
    		mean=mean, std=std)
		# load raw images transformer
		raw_transform = transformer.raw_transform()

    # forward pass
    inp = torch.from_numpy(trainingInput)
    out = net(inp)
