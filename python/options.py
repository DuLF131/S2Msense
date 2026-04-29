import argparse

class Options():
    def initialize(self):
        parser = argparse.ArgumentParser(description='PyTorch ResNet18 Example')
        parser.add_argument('--Epoch', type=int, default=200, help='the starting epoch count')
        parser.add_argument('--model', type=str, default='resnet18', help='The model to be trained')

        args = parser.parse_args()

        return args
