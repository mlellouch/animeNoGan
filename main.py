import torch
import models
import preprocessing
import torchvision.transforms as transforms
import random_transforms
from torch.utils.data import Dataset, DataLoader
import dataset
import train
import csv
import os
import time
import criterions


def save_data(filepath, train_loss, val_loss):
    with open(filepath, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=['epoch', 'train_loss', 'val_loss'])
        writer.writeheader()
        for i in range(len(train_loss)):
            row = {
                'epoch': i+1,
                'train_loss': train_loss[i],
                'val_loss': val_loss[i]
            }
            writer.writerow(row)


OUTPUT_DIR = os.curdir


def run_test(test_name, model, criterion, optimizer, lr_scheduler, train_dataloader, val_dataloader, epochs, global_transform=None, notebook=True, outdir=OUTPUT_DIR, unnormalize=False, vae=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    trainer = train.Trainer(
        model=model,
        device=device,
        criterion=criterion,
        optimizer=optimizer,
        lr_scheduler=lr_scheduler,
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader,
        epochs=epochs,
        notebook=notebook)
    output_dir = os.path.join(outdir, test_name)
    train_loss, val_loss, _ = trainer.run_trainer()
    os.makedirs(output_dir, exist_ok=True)
    save_data(os.path.join(output_dir, "results.csv"), train_loss, val_loss)
    torch.save(model.state_dict(), os.path.join(output_dir, f"model_{time.strftime('%Y_%m_%d-%H_%M.pth')}"))
    trainer.calculate_example_images(output_dir, global_transform, unnormalize=unnormalize, vae=vae)


train_episodes = [
  './dragon ball/EP.70.480p.mp4',
  './dragon ball/EP.71.v0.480p.mp4',
  './dragon ball/EP.72.480p.mp4',
  './dragon ball/EP.74.480p.mp4',
  './dragon ball/EP.78.720p.mp4',
  './dragon ball/EP.80.480p.mp4',
  './dragon ball/EP.81.480p.mp4',
  './dragon ball/EP.85.480p.mp4',
  './dragon ball/EP.86.v0.480p.mp4',
  './dragon ball/EP.87.480p.mp4',
  './dragon ball/EP.96.v0.480p.mp4',
  './dragon ball/EP.98.v0.480p.mp4',
]

val_episode = [
  './dragon ball/EP.73.480p.mp4',
]

if __name__ == '__main__':
    model = models.get_vae()
    # model.load_state_dict(torch.load('../../gdrive/MyDrive/anime/cpu_Epoch_28_Train_loss_25425.9503_Test_loss_25172.4120.pth'))
    model.eval()
    global_transforms = transforms.Compose([transforms.Resize((128, 128)), transforms.ToTensor()])
    random_trans = random_transforms.RandomTransform(flip=0.5, rotate=0.1, color_jitter=True, blur_operations_avg=0.5, return_gt_image_percent=0.03)
    inference_transform = transforms.Compose([transforms.Resize((128, 128)), transforms.ToTensor()])
    train_dataset, val_dataset = dataset.build_image_couple_dataset(global_transforms, random_trans)
    run_test(
        test_name="vae_with_augmentation",
        model=model,
        criterion=criterions.VAELoss(),
        optimizer=torch.optim.SGD(model.parameters(), lr=0.0001, momentum=0.9),
        train_dataloader=DataLoader(train_dataset, batch_size=4, shuffle=True),
        val_dataloader=DataLoader(val_dataset, batch_size=4, shuffle=True),
        lr_scheduler=None,
        global_transform=inference_transform,
        epochs=5,
        notebook=False,
        unnormalize=False,
        vae=True
    )




