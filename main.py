import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import SVD

def main():
    df = pd.read_csv("data/steam.csv")
    df = SVD.runSVD(df) #TODO: Implement Singular Value Decomposition to reduce cols in DataFrame

if __name__ == '__main__':
    main()