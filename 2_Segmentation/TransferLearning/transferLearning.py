import torchvision.models as models



learn = Learner(dls, # dataloader
                flower_model, #pretrained model
                metrics=[accuracy],
                opt_func= SGD,
                loss_func=nn.CrossEntropyLoss())
