# -*- coding: utf-8 -*-
"""hw2_319003323_train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vkW9bjPTJWvF2c_WMz5vQwGZlJ8NshFr
"""

from torch.utils.data import Dataset
import os
import random
import numpy as np
import matplotlib.pyplot as plt
import torchvision
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torchvision import datasets

LATENT_DIM = 2  # latent space dimension
ROOT = './data'  # directory to save coloredMNIST dataset
LR = 1e-3  # learning rate
input_size = 28 * 28 * 3


continuous_model_name = 'continuous_vae'
file_name= continuous_model_name + ".pkl"


domain= 'ColoredMNIST_Q1'
colored_mnist_dir = os.path.join(ROOT, domain)

try:
    os.makedirs(colored_mnist_dir)
except OSError as error:
    pass



device = 'cuda' if torch.cuda.is_available() else 'cpu'

"""# **Color MNIST**"""

from torch.utils.data import Dataset
import os
import random
import matplotlib.pyplot as plt
import torch

from torchvision import transforms
from torchvision import datasets

LATENT_DIM = 2  # latent space dimension
ROOT = './data'  # directory to save coloredMNIST dataset
LR = 1e-3  # learning rate


def is_colored_mnist_exists():
    """
    Check if coloredMNIST dataset exists in the given directory
    :return: True if exists, False otherwise
    """
    if (os.path.exists(os.path.join(colored_mnist_dir, 'train.pt')) and os.path.exists(os.path.join(colored_mnist_dir, 'test.pt'))):
        return True
    return False


def is_pkl_exists(pkl_path):
    """
    Check if pkl file exists in the given directory
    :param pkl_path: path to pkl file
    :return: True if exists, False otherwise
    """
    if os.path.exists(pkl_path):
        return True
    return False


def get_data():
    """
    Get the colored data from the given directory
    :return: train and test data
    """
    # coloredMNIST Dataset
    train_dataset = ColoredMNIST(env='train')
    test_dataset = ColoredMNIST(env='test')
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)
    test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=64, shuffle=False)

    return train_loader, test_loader


class ColoredMNIST(datasets.VisionDataset):

    def __init__(self, env='train', transform=None, target_transform=None):
        super(ColoredMNIST, self).__init__(ROOT, transform=transform, target_transform=target_transform)
        if not is_colored_mnist_exists():
            self.prepare_colored_mnist()
        if env in ['train', 'test']:
            self.data_label_tuples = torch.load(os.path.join(ROOT, 'ColoredMNIST_Q1', env) + '.pt')
        else:
            raise RuntimeError(f'{env} env unknown. Valid envs are train, test')

    def __getitem__(self, index):
        img, target = self.data_label_tuples[index]

        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return img, target

    def __len__(self):
        return len(self.data_label_tuples)

    def color_digits(self,img):
        """
        Color the digits in the image
        :param img: image to color
        :return: colored image
        """
        img = img[0]
        h, w = img.shape
        arr = torch.reshape(img, [h, w, 1])

        options = [0,1,2,3,4,5,6,7,8,9]
        choice = random.choice(options)

        if choice == 0:  # red
            arr = torch.cat((arr, torch.zeros((h, w, 2))), dim=2)
        elif choice == 1:  # green
            arr = torch.cat((torch.zeros((h, w, 1)), arr, torch.zeros((h, w, 1))), dim=2)
        elif choice == 2:  # blue
            arr = torch.cat((torch.zeros((h, w, 2)), arr), dim=2)
        elif choice == 3:  # yellow
            arr = torch.cat((arr, arr, torch.zeros((h, w, 1))), dim=2)
        elif choice == 4:  # purple
            z = 128 / 255
            arr = torch.cat((arr * z, torch.zeros((h, w, 1)), arr * z), dim=2)
        elif choice == 5:  # orange
            g = 165 / 255
            arr = torch.cat((arr, arr * g, torch.zeros((h, w, 1))), dim=2)
        elif choice == 6:  # brown
            r = 139 / 255
            g = 69 / 255
            b = 19 / 255
            arr = torch.cat((arr * r, arr * g, arr * b), dim=2)
        elif choice == 7:  # pink
            g = 192 / 255
            b = 203 / 255
            arr = torch.cat((arr, arr * g, arr * b), dim=2)
        elif choice == 8:  # cyan
            arr = torch.cat((torch.zeros((h, w, 1)), arr, arr), dim=2)
        else:  # white
            arr = torch.cat((arr, arr, arr), dim=2)

        arr = arr.permute(2, 0, 1)
        return arr

    def prepare_colored_mnist(self):
        """
        Prepare the coloredMNIST dataset
        :return:
        """
        if is_colored_mnist_exists():
            print('Colored MNIST dataset already exists')

        else:
            print('Preparing Colored MNIST')
            train_mnist = datasets.mnist.MNIST(ROOT, train=True, transform=transforms.ToTensor(), download=True)
            test_mnist = datasets.mnist.MNIST(ROOT, train=False, transform=transforms.ToTensor(), download=True)

            train_set = []
            test_set = []
            for idx, (im, label) in enumerate(train_mnist):
                train_set.append((self.color_digits(im), label))

            for idx, (im, label) in enumerate(test_mnist):
                test_set.append((self.color_digits(im), label))

            torch.save(train_set, os.path.join(colored_mnist_dir, 'train.pt'))
            torch.save(test_set, os.path.join(colored_mnist_dir, 'test.pt'))


def plot_dataset_digits(dataset):
    """
    Plot the dataset digits in color to check it was colored correctly
    :param dataset: colored dataset created by the ColoredMNIST class
    :return:
    """
    fig = plt.figure(figsize=(13, 8))
    columns = 6
    rows = 3
    # ax enables access to manipulate each of subplots
    ax = []

    for i in range(columns * rows):
        img, label = dataset[i]
        img = img.permute(1, 2, 0).detach().numpy()  # convert to numpy array for plotting

        # create subplot and append to ax
        ax.append(fig.add_subplot(rows, columns, i + 1))
        ax[-1].set_title("Label: " + str(label))  # set title for each subplot according to the label
        plt.imshow(img)

    plt.show()



"""# **Plot functions**"""

def plot_loss(train_loss, test_loss, name):
    """
    Plot the loss for the train and test set
    :param train_loss: list of train loss for each epoch
    :param test_loss: list of test loss for each epoch
    :param name: name of the model
    """
    plt.plot(train_loss, label='train loss')
    plt.plot(test_loss, label='test loss')
    plt.legend()
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.title("NELBO as a function of epoch for the {} model".format(name))
    plt.savefig('{}_loss.png'.format(name))
    plt.show()



def plot_latent(autoencoder, data, model_name=continuous_model_name, train=True):
    """
    Plot the latent space of the model for the train or test set
    :param autoencoder: the model
    :param data: train or test set
    :param model_name: name of the model
    :param train: boolean to know if we are plotting the train or test set
    :return:
    """
    for i, (x, y) in enumerate(data):
        z = autoencoder.encoder(x.to(device))
        z = z.to('cpu').detach().numpy()
        plt.scatter(z[:, 0], z[:, 1], c=y, cmap='tab10')
    plt.colorbar()
    if train:
        plt.title("Latent space of the {} on the train set".format(model_name))
    else:
        plt.title("Latent space of the {} on the test set".format(model_name))
    plt.show()


def plot_reconstructed(autoencoder, r0=(-5, 10), r1=(-10, 5), n=12, model_name=continuous_model_name):
    """
    Plot the reconstructed images of the model
    :param autoencoder: the model
    :param r0: range of the first latent dimension
    :param r1: range of the second latent dimension
    :param n: number of images to plot in each dimension
    :param model_name: name of the model
    :return:
    """
    img = []
    for i, z2 in enumerate(np.linspace(r1[1], r1[0], n)):
        for j, z1 in enumerate(np.linspace(*r0, n)):
            z = torch.Tensor([[z1, z2]]).to(device)
            x_hat = autoencoder.decoder(z)
            img.append(x_hat)

    img = torch.cat(img)
    img = torchvision.utils.make_grid(img, nrow=12).permute(1, 2, 0).detach().cpu().numpy()
    plt.imshow(img, extent=[*r0, *r1])
    plt.title("Reconstructed images of the {}".format(model_name))
    plt.show()

"""# **Continuous VAE**"""

class Encoder(nn.Module):
    def __init__(self, latent_dims):
        super(Encoder, self).__init__()
        self.linear1 = nn.Linear(input_size, 512)  # 28*28*3 = 2352 the size of the image after the colorization
        self.to_mean_logvar = nn.Linear(512, 2 * latent_dims)  # 2 * latent_dims because we have mean and logvar
        self.latent_dims = latent_dims

    def reparametrization_trick(self, mu, log_var):
        # Using re-parameterization trick to sample from a gaussian
        eps = torch.randn_like(log_var)  # eps ~ N(0, I)
        return mu + torch.exp(log_var / 2) * eps  # z = mu + sigma * eps

    def forward(self, x):
        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.linear1(x))
        mu, log_var = torch.split(self.to_mean_logvar(x), self.latent_dims, dim=-1)
        self.kl = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        res = self.reparametrization_trick(mu, log_var)
        return res


class Decoder(nn.Module):
    def __init__(self, latent_dims):
        super(Decoder, self).__init__()
        self.linear1 = nn.Linear(latent_dims, 512)
        self.linear2 = nn.Linear(512, input_size)

    def forward(self, z):
        z = F.relu(self.linear1(z))
        z = torch.sigmoid(self.linear2(z))
        res = z.reshape((-1, 3, 28, 28))
        return res


class ContinuousVAE(nn.Module):
    def __init__(self, latent_dims):
        super().__init__()
        self.encoder = Encoder(latent_dims).cuda()
        self.decoder = Decoder(latent_dims).cuda()

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

    def train_model(self, train_data, test_data, name= continuous_model_name, epochs=20):
        """
        Train and evaluate the model on the train and test set
        :param train_data: train set of colored MNIST
        :param test_data: test set of colored MNIST
        :param epochs: number of epochs
        :return:
        """
        opt = torch.optim.Adam(self.parameters(), lr=LR)
        train_loss = []
        test_loss = []
        for epoch in range(epochs):
            running_train_loss = 0
            running_test_loss = 0
            # ------------------- train -------------------
            self.train()
            for i, (im, label) in enumerate(train_data):
              im = im.to(device)

              opt.zero_grad()
              x_hat = self(im)

              loss = F.binary_cross_entropy(x_hat, im, reduction='sum') + self.encoder.kl  # BCE + KL
              loss.backward()
              opt.step()
              running_train_loss += loss.item()
              if i % 100 == 0:
                  print(f'\rEpoch {epoch} Batch {i} Train Loss {loss.item()}', end='')
            train_loss.append(running_train_loss / len(train_data.dataset))

            # ------------------- test -------------------
            self.eval()
            with torch.no_grad():
                for i, (im, label) in enumerate(test_data):
                  im = im.to(device)
                  x_hat = self(im)
                  loss = F.binary_cross_entropy(x_hat, im, reduction='sum') + self.encoder.kl
                  running_test_loss += loss.item()
                  if i % 100 == 0:
                      print(f'\rEpoch {epoch} Batch {i} Test Loss {loss.item()}', end='')
            test_loss.append(running_test_loss / len(test_data.dataset))

        plot_loss(train_loss, test_loss, name)
        torch.save(self.state_dict(), name+".pkl")

train, test = get_data()
plot_dataset_digits(train.dataset)

VAE = ContinuousVAE(LATENT_DIM).to(device)
VAE.train_model(train, test, epochs=20)
plot_latent(VAE, train, train=True)
plot_latent(VAE, test, train=False)
plot_reconstructed(VAE)

def plot_3d_reconstructed(autoencoder, r0=(-5, 10), r1=(-10, 5), r2=(-5, 10), n=12, model_name=continuous_model_name):
    
    for k, z3 in enumerate(np.linspace(*r2, n)):
      img = []
      for i, z2 in enumerate(np.linspace(r1[1], r1[0], n)):
          for j, z1 in enumerate(np.linspace(*r0, n)):
            
              z = torch.Tensor([[z1, z2,z3]]).to(device)
              x_hat = autoencoder.decoder(z)
              img.append(x_hat)

      img = torch.cat(img)
      img = torchvision.utils.make_grid(img, nrow=12).permute(1, 2, 0).detach().cpu().numpy()
      plt.imshow(img, extent=[*r0, *r1])
      plt.title("Reconstructed images of the {}, r2={}".format(model_name,z3))
      plt.show()

VAE3 = ContinuousVAE(3).to(device)
VAE3.train_model(train, test,name="Latent_3_continuous_vae", epochs=20)

plot_3d_reconstructed(VAE3, model_name="continuous_vae")

VAE5 = ContinuousVAE(5).to(device)
VAE5.train_model(train, test,name="Latent_5_continuous_vae", epochs=20)

VAE10 = ContinuousVAE(10).to(device)
VAE10.train_model(train, test,name="Latent_10_continuous_vae", epochs=20)

VAE25 = ContinuousVAE(25).to(device)
VAE25.train_model(train, test,name="Latent_25_continuous_vae", epochs=20)

VAE50 = ContinuousVAE(50).to(device)
VAE50.train_model(train, test,name="Latent_50_continuous_vae", epochs=20)

"""# **Discrete VAE** """

discrete_model_name = 'discrete_vae'

colored_mnist_dir = os.path.join(ROOT, 'ColoredMNIST_Q1')




temp = 5.0
hard = True
temp_min = 0.5
ANNEAL_RATE = 0.000003
input_size = 28 * 28 * 3


def reconstruct_grid_discrete(model,N,K):
    ind = torch.zeros(N, 1).long()
    to_generate = torch.zeros(K, K, N, K)

    for i in range(K):
        for j in range(K):
            ind[0] = i
            ind[1] = j
            z = F.one_hot(ind, num_classes=K).squeeze(1)

            to_generate[K-1-i][j] = z


    generate = to_generate.view(-1, K * N).to(device)

    reconst_images = model.decoder(generate)
    reconst_images = reconst_images.view(reconst_images.size(0), 3, 28, 28).detach()

    grid_img = torchvision.utils.make_grid(reconst_images, nrow=K).permute(1, 2, 0).cpu().numpy() * 255
    grid_img = grid_img.astype(np.uint8)
    plt.imshow(grid_img, extent=[0,19,0,19])
    plt.title("Reconstructed images of the {}".format(discrete_model_name))

    plt.savefig('discrete_grid.png')
    plt.show()

def plot_digit(model,k0,k1,N,K):
    ind = torch.zeros(N, 1).long()
    to_generate = torch.zeros(1, N, K)
    ind[0] = k0
    ind[1] = k1
    z = F.one_hot(ind, num_classes=K).squeeze(1)
    to_generate[0] = z
    generate = to_generate.view(-1, K * N)
    reconst_images = model.decoder(generate)
    reconst_images = reconst_images.view(reconst_images.size(0), 3, 28, 28).detach()
    plt.imshow(reconst_images[0].permute(1, 2, 0).numpy())
    plt.show()


def reconstruct_grid_discrete_3d(model,N,K):
    ind = torch.zeros(N, 1).long()
    for k in range(K):
      to_generate = torch.zeros(K, K, N, K)
      for i in range(K):
        for j in range(K):
            ind[0] = k
            ind[1] = i
            ind[2] = j
            z = F.one_hot(ind, num_classes=K).squeeze(1)

            to_generate[i][j] = z


      generate = to_generate.view(-1, K * N).to(device)

      reconst_images = model.decoder(generate)
      reconst_images = reconst_images.view(reconst_images.size(0), 3, 28, 28).detach()

      grid_img = torchvision.utils.make_grid(reconst_images, nrow=K).permute(1, 2, 0).cpu().numpy() * 255
      grid_img = grid_img.astype(np.uint8)
      plt.imshow(grid_img, extent=[0,19,0,19])
      plt.title("Reconstructed images of the {} K3={}".format(discrete_model_name,k))

      plt.savefig('discrete_grid.png')
      plt.show()

def gumbel_softmax_sample(logits, tau=1, eps=1e-20):
    """
    Draw a sample from the Gumbel-Softmax distribution.
    :param logits: [torch.Tensor] unnormalized log-probs
    :param tau: [float] non-negative scalar temperature
    :param eps: [float] for numerical stability
    :return:
    """
    U = torch.rand(logits.size()).float()
    gumbel_noise = - torch.log(eps - torch.log(U + eps)).to(device)
    y = logits + gumbel_noise
    return F.softmax(y / tau, dim=-1)


def gumbel_softmax(logits, tau=1, hard=False):
    """
    Sample from the Gumbel-Softmax distribution and optionally discretize.
    :param logits: [torch.Tensor] unnormalized log-probs
    :param tau: [float] non-negative scalar temperature
    :param hard: [bool] if True, take argmax, but differentiate w.r.t. soft sample y
    :return: [torch.Tensor] sample from the Gumbel-Softmax distribution.
    """
    batch_size, N, K = logits.size()
    y_soft = gumbel_softmax_sample(logits.view(batch_size * N, K), tau=tau)

    if hard:
        k = torch.argmax(y_soft, dim=-1)
        y_hard = F.one_hot(k, num_classes=K)
        y = y_hard - y_soft.detach() + y_soft
    else:
        y = y_soft

    return y.reshape(batch_size, N * K)


# Reconstruction + KL divergence losses summed over all elements and batch
def loss_function(recon_x, x, qy):
    BCE = F.binary_cross_entropy(recon_x, x.view(-1, input_size), reduction='sum') / x.shape[0]

    log_ratio = torch.log(qy * qy.size(-1) + 1e-20)
    KLD = torch.sum(qy * log_ratio, dim=-1).mean()

    return BCE + KLD
# loss = F.binary_cross_entropy(x_hat, im, reduction='sum') + self.encoder.kl

class DiscreteVAE(nn.Module):
    def __init__(self, latent_dim, categorical_dim):
        super(DiscreteVAE, self).__init__()

        self.fc1 = nn.Linear(input_size, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, latent_dim * categorical_dim)

        self.fc4 = nn.Linear(latent_dim * categorical_dim, 256)
        self.fc5 = nn.Linear(256, 512)
        self.fc6 = nn.Linear(512, input_size)

        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

        self.N = latent_dim
        self.K = categorical_dim

    def encoder(self, x):
        h1 = self.relu(self.fc1(x))
        h2 = self.relu(self.fc2(h1))
        return self.relu(self.fc3(h2))

    def decoder(self, z):
        h4 = self.relu(self.fc4(z))
        h5 = self.relu(self.fc5(h4))
        return self.sigmoid(self.fc6(h5))

    def forward(self, x, temp, hard):
        q = self.encoder(x.view(-1, input_size))
        q_y = q.view(q.size(0), self.N, self.K)  # original latent space before discretization
        z = gumbel_softmax(q_y, temp, hard)

        return self.decoder(z), F.softmax(q_y, dim=-1).reshape(q.size(0)*self.N, self.K)

    def train_discrete_model(self,train_data,test_data, num_epochs=20, temp=1.0, hard=False,name= discrete_model_name):
        train_loss = []
        test_loss = []

        optimizer = torch.optim.Adam(self.parameters(), lr=LR)
        for epoch in range(num_epochs):
            running_train_loss = 0
            running_test_loss = 0
            # ------------------- train -------------------
            self.train()
            for batch_idx, (im, _) in enumerate(train_data):
              im= im.to(device)
              optimizer.zero_grad()
              x_hat, qy = self(im, temp, hard)
              loss = loss_function(x_hat, im, qy)
              loss.backward()
              optimizer.step()
              running_train_loss += loss.item()
              if batch_idx % 100 == 0:
                  temp = np.maximum(temp * np.exp(-ANNEAL_RATE * batch_idx), temp_min)
                  print(f'\rEpoch {epoch} Batch {batch_idx} Train Loss: {loss.item()} Temp: {temp}', end='')
            train_loss.append(running_train_loss / len(train_data))

            # ------------------- test -------------------
            self.eval()
            with torch.no_grad():
                for i, (im, _) in enumerate(test_data):
                  im= im.to(device)
                  x_hat, qy = self(im, temp, hard)
                  loss = loss_function(x_hat, im, qy)
                  running_test_loss += loss.item()
                  if i % 100 == 0:
                      print(f'\rEpoch {epoch} Batch {i} Train Loss: {loss.item()} Temp: {temp}', end='')
            test_loss.append(running_test_loss / len(test_data))

        plot_loss(train_loss, test_loss, name)
        torch.save(self.state_dict(), name + ".pkl")

N = 2  # number of discrete latent variables
K = 10  # number of discrete latent variables values
vae= DiscreteVAE(N, K).to(device)
vae.train_discrete_model(train, test, num_epochs=20, temp=temp, hard=hard,name= "N2_hard"+discrete_model_name)
reconstruct_grid_discrete(vae,N,K)

N = 2  # number of discrete latent variables
K = 10  # number of discrete latent variables values
vae= DiscreteVAE(N, K).to(device)
vae.train_discrete_model(train, test, num_epochs=20, temp=temp, hard=False,name= "N2_soft"+discrete_model_name)
reconstruct_grid_discrete(vae,N,K)

N = 3  # number of discrete latent variables
K = 10  # number of discrete latent variables values
vae= DiscreteVAE(N, K).to(device)
vae.train_discrete_model(train, test, num_epochs=20, temp=temp, hard=hard,name= "N3_hard"+discrete_model_name)
reconstruct_grid_discrete_3d(vae,N,K)

N = 3  # number of discrete latent variables
K = 10  # number of discrete latent variables values
vae= DiscreteVAE(N, K).to(device)
vae.train_discrete_model(train, test, num_epochs=20, temp=temp, hard=False,name= "N3_soft"+discrete_model_name)
reconstruct_grid_discrete_3d(vae,N,K)

"""# **Joint VAE**"""

N=2
K=10
LR = 1e-3
input_size = 28 * 28 * 3
ANNEAL_RATE = 0.000003
temp_min = 0.5
temp =5.0
joint_model_name = 'joint_vae'


def reconstruct_grid_joint(model):
    r0 = (-5, 10)
    r1 = (-10, 5)
    n = K

    to_generate_con = torch.zeros(K, K,2, 1)
    to_generate_dis = torch.zeros(K, K, N, K)

    ind1 = torch.zeros(2, 1).long()
    for i, z2 in enumerate(np.linspace(r1[1], r1[0], n)):
        for j, z1 in enumerate(np.linspace(*r0, n)):
            ind1[0] = torch.Tensor([z1])
            ind1[1] = torch.Tensor([z2])
            to_generate_con[i, j] = ind1

    ind = torch.zeros(N, 1).long()
    for i in range(K):
        for j in range(K):
            ind[0] = i
            ind[1] = j
            z = F.one_hot(ind, num_classes=K).squeeze(1)
            to_generate_dis[K-1-i][j] = z


    to_generate = torch.cat((to_generate_dis, to_generate_con), dim=3).to(device)
    generate = to_generate.view(-1, K * N +2)

    reconst_images = model.decoder(generate)
    reconst_images = reconst_images.view(reconst_images.size(0), 3, 28, 28).detach()

    grid_img = torchvision.utils.make_grid(reconst_images, nrow=K).permute(1, 2, 0).cpu().numpy() * 255
    grid_img = grid_img.astype(np.uint8)
    plt.imshow(grid_img)
    plt.title("Reconstructed images of the {}".format(joint_model_name))

    plt.savefig('discrete_grid.png')
    plt.show()

class EncoderContinuous(nn.Module):
    def __init__(self, latent_dims):
        super(EncoderContinuous, self).__init__()
        self.linear1 = nn.Linear(input_size, 512)  # 28*28*3 = 2352 the size of the image after the colorization
        self.to_mean_logvar = nn.Linear(512, 2 * latent_dims)  # 2 * latent_dims because we have mean and logvar
        self.latent_dims = latent_dims

    def reparametrization_trick(self, mu, log_var):
        # Using re-parameterization trick to sample from a gaussian
        eps = torch.randn_like(log_var)  # eps ~ N(0, I)
        return mu + torch.exp(log_var / 2) * eps  # z = mu + sigma * eps

    def forward(self, x):
        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.linear1(x))
        mu, log_var = torch.split(self.to_mean_logvar(x), self.latent_dims, dim=-1)
        # self.kl = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        # res = self.reparametrization_trick(mu, log_var)
        return mu, log_var


class EncoderDiscrete(nn.Module):
    def __init__(self, latent_dim, categorical_dim):
        super(EncoderDiscrete, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, latent_dim * categorical_dim)
        self.N = latent_dim
        self.K = categorical_dim
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = x.view(-1, input_size)
        h1 = self.relu(self.fc1(x))
        h2 = self.relu(self.fc2(h1))
        h3 = self.relu(self.fc3(h2))
        return h3

    def reparametrization_trick(self,q, temp, hard):
        q_y = q.view(q.size(0), self.N, self.K)
        return gumbel_softmax(q_y, temp, hard)

def loss_function_joint(recon_x, x, q, mu, log_var):
    recon_loss = F.binary_cross_entropy(recon_x, x.view(-1, input_size), reduction='sum')
    KLC = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    qy = q.view(q.size(0), N, K)
    log_ratio = torch.log(qy * qy.size(-1) + 1e-20)
    KLD = torch.sum(qy * log_ratio, dim=-1).sum()
    return recon_loss + KLD + KLC


class JointVAE(nn.Module):
    def __init__(self, latent_dim_continuous, N, K):
        super(JointVAE, self).__init__()
        self.encoder_continuous = EncoderContinuous(latent_dim_continuous)
        self.encoder_discrete = EncoderDiscrete(N, K)
        self.latent_dim=latent_dim_continuous+K*N
        self.fc4 = nn.Linear(self.latent_dim, 256)
        self.fc5 = nn.Linear(256, 512)
        self.fc6 = nn.Linear(512, input_size)

    def decoder(self, z):
        h4 = nn.ReLU()(self.fc4(z))
        h5 = nn.ReLU()(self.fc5(h4))
        return nn.Sigmoid()(self.fc6(h5))

    def forward(self, x, temp, hard):
        q= self.encoder_discrete(x)
        z1 = self.encoder_discrete.reparametrization_trick(q, temp, hard)
        mu, log_var = self.encoder_continuous(x)
        z2 = self.encoder_continuous.reparametrization_trick(mu, log_var)
        joint_z = torch.cat((z1, z2), dim=1)
        return self.decoder(joint_z), q, mu, log_var

    def train_joint_model(self,train_data,test_data, num_epochs=20, temp=1.0, hard=False, name= joint_model_name):
        train_loss = []
        test_loss = []

        optimizer = torch.optim.Adam(self.parameters(), lr=LR)
        for epoch in range(num_epochs):
            running_train_loss = 0
            running_test_loss = 0
            # ------------------- train -------------------
            self.train()
            for batch_idx, (im, _) in enumerate(train_data):
              im = im.to(device)
              optimizer.zero_grad()
              x_hat, q, mu, log_var= self(im, temp, hard)
              loss = loss_function_joint(x_hat, im, q, mu, log_var)
              loss.backward()
              optimizer.step()
              running_train_loss += loss.item()
              if batch_idx % 100 == 0:
                  temp = np.maximum(temp * np.exp(-ANNEAL_RATE * batch_idx), temp_min)
                  print(f'\rEpoch {epoch} Batch {batch_idx} Train Loss: {loss.item()/len(im)} Temp: {temp}', end='')
            train_loss.append(running_train_loss / len(train_data.dataset))

            # ------------------- test -------------------
            self.eval()
            with torch.no_grad():
                for i, (im, _) in enumerate(test_data):
                  im = im.to(device)
                  x_hat, q, mu, log_var = self(im, temp, hard)
                  loss = loss_function_joint(x_hat, im, q, mu, log_var)
                  running_test_loss += loss.item()
                  if i % 100 == 0:
                      print(f'\rEpoch {epoch} Batch {i} Train Loss: {loss.item()/len(im)} Temp: {temp}', end='')
            test_loss.append(running_test_loss / len(test_data.dataset))

        reconstruct_grid_joint(self)
        plot_loss(train_loss, test_loss, name)
        torch.save(self.state_dict(), name + ".pkl")

vae= JointVAE(2,N, K).to(device)
temp = 3.0
hard=False
optimizer = torch.optim.Adam(vae.parameters(), lr=LR)

vae.train_joint_model(train,test, num_epochs=20, temp=temp, hard=hard,name="soft"+joint_model_name)
reconstruct_grid_joint(vae)

vae= JointVAE(2,N, K).to(device)
temp = 3.0
optimizer = torch.optim.Adam(vae.parameters(), lr=LR)

vae.train_joint_model(train,test, num_epochs=20, temp=temp, hard=True,name="hard"+joint_model_name)
reconstruct_grid_joint(vae)

def plot_digit_joint(model,k0,k1,N,K,z1,z2):
    ind = torch.zeros(N, 1).long()
    to_generate_dis = torch.zeros(1, N, K)
    ind[0] = k0
    ind[1] = k1
    ind1 = torch.zeros(N, 1).long()
    z = F.one_hot(ind, num_classes=K).squeeze(1)
    to_generate_dis[0] = z
    to_generate_con =  torch.zeros(1,2, 1)
    ind1[0] = torch.Tensor([z1])
    ind1[1] = torch.Tensor([z2])
    to_generate_con[0] = ind1
    to_generate = torch.cat((to_generate_dis, to_generate_con), dim=2).to(device)
    generate = to_generate.view(-1, K * N+2)
    reconst_images = model.decoder(generate)
    reconst_images = reconst_images.view(reconst_images.size(0), 3, 28, 28).detach()
    plt.imshow(reconst_images[0].permute(1, 2, 0).cpu().numpy())
    plt.title("k0={}, k1={}, z1={}, z2={}".format(k0,k1,z1,z2))
    plt.show()

plot_digit_joint(vae,1,5,N,K,0.1,-5.0)

plot_digit_joint(vae,0,9,N,K,10.0,-5.0)

plot_digit_joint(vae,0,0,N,K,10.0,-5.0)

plot_digit_joint(vae,0,9,N,K,-5.0,-5.0)

plot_digit_joint(vae,0,9,N,K,-5.0,10.0)

plot_digit_joint(vae,1,1,N,K,-5.0,10.0)

