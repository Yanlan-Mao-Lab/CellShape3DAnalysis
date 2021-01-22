import torch

checkpoint_path = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/2_Segmentation/TransferLearning/PreTrainedModels/unet3d-arabidopsis-ovules-confocal-ds2x.pytorch'
state = torch.load(checkpoint_path, map_location='cpu')
print (state)
state['model_state_dict']
