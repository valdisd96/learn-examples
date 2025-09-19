import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
random.seed(0)
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Lasso, Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def plot_polynomial_regression(model, X, Y, degree, X_test=None, Y_test=None):
    """
    Plots the original data points and the polynomial regression curve,
    optionally including test data points.

    Args:
      model: The trained scikit-learn model object.
      X: Input features (list or numpy array).
      Y: Input labels (list or numpy array).
      degree: The degree of the polynomial used for training.
      X_test: Optional test set features (list or numpy array).
      Y_test: Optional test set labels (list or numpy array).
    """
    X = np.array(X).reshape(-1, 1)
    Y = np.array(Y)

    # Generate predicted values for plotting the curve
    X_plot = np.linspace(np.min(X), np.max(X), 100).reshape(-1, 1)
    poly = PolynomialFeatures(degree=degree)
    X_plot_poly = poly.fit_transform(X_plot) # Fit on plot data range

    Y_plot_poly = model.predict(X_plot_poly)

    # Plot the original points
    plt.scatter(X, Y, color='blue', label='Original Data')

    # Plot the polynomial regression curve
    plt.plot(X_plot, Y_plot_poly, color='red', label=f'Polynomial Regression (degree {degree})')

    # Plot test data points if provided
    if X_test is not None and Y_test is not None:
        X_test = np.array(X_test).reshape(-1, 1)
        Y_test = np.array(Y_test)
        plt.scatter(X_test, Y_test, color='orange', marker='^', label='Test Data')


    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Polynomial Regression (Degree {degree})')
    plt.legend()
    plt.grid(True)

    # Set plot bounds based on X and Y
    plt.xlim(np.min(X), np.max(X))
    plt.ylim(np.min(Y), np.max(Y))

    plt.show()
    
