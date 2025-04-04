import numpy as np
from scipy.io import loadmat
from scipy.optimize import minimize
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.svm import SVC

def preprocess():
    """ 
     Input:
     Although this function doesn't have any input, you are required to load
     the MNIST data set from file 'mnist_all.mat'.

     Output:
     train_data: matrix of training set. Each row of train_data contains 
       feature vector of a image
     train_label: vector of label corresponding to each image in the training
       set
     validation_data: matrix of training set. Each row of validation_data 
       contains feature vector of a image
     validation_label: vector of label corresponding to each image in the 
       training set
     test_data: matrix of training set. Each row of test_data contains 
       feature vector of a image
     test_label: vector of label corresponding to each image in the testing
       set
    """

    mat = loadmat('basecode/mnist_all.mat')  # loads the MAT object as a Dictionary

    n_feature = mat.get("train1").shape[1]
    n_sample = 0
    for i in range(10):
        n_sample = n_sample + mat.get("train" + str(i)).shape[0]
    n_validation = 1000
    n_train = n_sample - 10 * n_validation

    # Construct validation data
    validation_data = np.zeros((10 * n_validation, n_feature))
    for i in range(10):
        validation_data[i * n_validation:(i + 1) * n_validation, :] = mat.get("train" + str(i))[0:n_validation, :]

    # Construct validation label
    validation_label = np.ones((10 * n_validation, 1))
    for i in range(10):
        validation_label[i * n_validation:(i + 1) * n_validation, :] = i * np.ones((n_validation, 1))

    # Construct training data and label
    train_data = np.zeros((n_train, n_feature))
    train_label = np.zeros((n_train, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("train" + str(i)).shape[0]
        train_data[temp:temp + size_i - n_validation, :] = mat.get("train" + str(i))[n_validation:size_i, :]
        train_label[temp:temp + size_i - n_validation, :] = i * np.ones((size_i - n_validation, 1))
        temp = temp + size_i - n_validation

    # Construct test data and label
    n_test = 0
    for i in range(10):
        n_test = n_test + mat.get("test" + str(i)).shape[0]
    test_data = np.zeros((n_test, n_feature))
    test_label = np.zeros((n_test, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("test" + str(i)).shape[0]
        test_data[temp:temp + size_i, :] = mat.get("test" + str(i))
        test_label[temp:temp + size_i, :] = i * np.ones((size_i, 1))
        temp = temp + size_i

    # Delete features which don't provide any useful information for classifiers
    sigma = np.std(train_data, axis=0)
    index = np.array([])
    for i in range(n_feature):
        if (sigma[i] > 0.001):
            index = np.append(index, [i])
    train_data = train_data[:, index.astype(int)]
    validation_data = validation_data[:, index.astype(int)]
    test_data = test_data[:, index.astype(int)]

    # Scale data to 0 and 1
    train_data /= 255.0
    validation_data /= 255.0
    test_data /= 255.0

    return train_data, train_label, validation_data, validation_label, test_data, test_label


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def blrObjFunction(initialWeights, *args):
    """
    blrObjFunction computes 2-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector (w_k) of size (D + 1) x 1 
        train_data: the data matrix of size N x D
        labeli: the label vector (y_k) of size N x 1 where each entry can be either 0 or 1 representing the label of corresponding feature vector

    Output: 
        error: the scalar value of error function of 2-class logistic regression
        error_grad: the vector of size (D+1) x 1 representing the gradient of
                    error function
    """
    train_data, labeli = args

    n_data = train_data.shape[0]
    # n_features = train_data.shape[1]
    # error = 0
    # error_grad = np.zeros((n_features + 1, 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    # Add bias term to the data
    X = np.hstack([np.ones((n_data, 1)), train_data])

    # Reshape initial weights to a column vector
    w_k = initialWeights.reshape(-1, 1)

    # Compute the sigmoid
    h = sigmoid(X.dot(w_k))

    # Compute error function
    error = (-1 / n_data) * np.sum(labeli * np.log(h) + (1 - labeli) * np.log(1 - h))

    # Compute the gradient
    error_grad = (1 / n_data) * X.T.dot(h - labeli)

    # Return error and flattened gradient
    return error, error_grad.flatten()


    # train_data = np.hstack((np.ones((n_data, 1)), train_data))

    # # This is the computation of the sigmoid function
    # z = np.dot(train_data, initialWeights)
    # theta = sigmoid(z)

    # # This is the computation of the error using cross-entropy loss
    # error = -np.sum(labeli * np.log(theta) + (1 - labeli) * np.log(1 - theta)) / n_data

    # # This is the computation of the error gradient
    # error_grad = np.dot(train_data.T, (theta - labeli)) / n_data

    # return error, error_grad


def blrPredict(W, data):
    """
     blrObjFunction predicts the label of data given the data and parameter W 
     of Logistic Regression
     
     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight 
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D
         
     Output: 
         label: vector of size N x 1 representing the predicted label of 
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    n_data = data.shape[0]  

    # Adding the bias term to the data
    data = np.hstack((np.ones((n_data, 1)), data))

    # This line is computing the posterior probabilities
    probabilities = sigmoid(np.dot(data, W))

    # PThis will predict the label with the highest probability and thus uses argmax
    label = np.argmax(probabilities, axis=1).reshape((n_data, 1))

    return label

def mlrObjFunction(params, *args):
    """
    mlrObjFunction computes multi-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights_b: the weight vector of size (D + 1) x 10
        train_data: the data matrix of size N x D
        Y: the label vector of size N x 10 where each entry can be either 0 or 1
                representing the label of corresponding feature vector

    Output:
        error: the scalar value of error function of multi-class logistic regression
        error_grad: the vector of size (D+1) x 10 representing the gradient of
                    error function
    """
    train_data, Y = args
    n_data = train_data.shape[0]
    n_features = train_data.shape[1]

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    
    # Modified n_classes to make it dynamic instead of static
    n_classes = Y.shape[1]

    params = params.reshape((n_features + 1, n_classes))

    # This aadd the bias term to the data
    train_data = np.hstack((np.ones((n_data, 1)), train_data))

    # Using the softmax function to compute theta (probabilities)
    theta = np.exp(np.dot(train_data, params))
    theta /= np.sum(theta, axis=1, keepdims=True)

    # The computes the error
    error = -np.sum(Y * np.log(theta)) / n_data

    # This computes the gradient
    error_grad = np.dot(train_data.T, (theta - Y)) / n_data

    return error, error_grad.flatten()


def mlrPredict(W, data):
    """
     mlrObjFunction predicts the label of data given the data and parameter W
     of Logistic Regression

     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D

     Output:
         label: vector of size N x 1 representing the predicted label of
         corresponding feature vector given in data matrix

    """
    n_data = data.shape[0]
    # Adding the bias term to the data
    data = np.hstack((np.ones((n_data, 1)), data))

    # Computing the posterior probabilities and returning the label with highest probability
    probabilities = np.exp(np.dot(data, W))
    probabilities /= np.sum(probabilities, axis=1, keepdims=True)
    label = np.argmax(probabilities, axis=1).reshape((n_data, 1))

    return label

if __name__ == "__main__":

    """
    Script for Logistic Regression
    """
    train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()
    
    # number of classes
    n_class = 10
    
    # number of training samples
    n_train = train_data.shape[0]
    
    # number of features
    n_feature = train_data.shape[1]
    
    Y = np.zeros((n_train, n_class))
    for i in range(n_class):
        Y[:, i] = (train_label == i).astype(int).ravel()
    
    # Logistic Regression with Gradient Descent
    W = np.zeros((n_feature + 1, n_class))
    initialWeights = np.zeros((n_feature + 1, 1))
    opts = {'maxiter': 100}
    for i in range(n_class):
        labeli = Y[:, i].reshape(n_train, 1)
        args = (train_data, labeli)
        nn_params = minimize(blrObjFunction, initialWeights.flatten(), jac=True, args=args, method='CG', options=opts)
        W[:, i] = nn_params.x.reshape((n_feature + 1,))
    
    # Find the accuracy on Training Dataset
    predicted_label = blrPredict(W, train_data)
    print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label == train_label).astype(float))) + '%')
    
    # Find the accuracy on Validation Dataset
    predicted_label = blrPredict(W, validation_data)
    print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label == validation_label).astype(float))) + '%')
    
    # Find the accuracy on Testing Dataset
    predicted_label = blrPredict(W, test_data)
    print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label == test_label).astype(float))) + '%')
    
    """
    Script for Support Vector Machine
    """
    
    print('\n\n--------------SVM-------------------\n\n')
    ##################
    # YOUR CODE HERE #
    ##################
    n_samples = 10000
    indices = np.random.choice(train_data.shape[0], n_samples, replace=False)
    reduced_train_data = train_data[indices, :]
    reduced_train_label = train_label[indices, :]

    print('\n\n--------------SVM- Linear------------------\n\n')
    linear_svm = SVC(kernel='linear')
    linear_svm.fit(reduced_train_data, reduced_train_label.ravel())
    print('Linear Kernel Accuracy:')
    print('Training:', linear_svm.score(train_data, train_label.ravel()))
    print('Validation:', linear_svm.score(validation_data, validation_label.ravel()))
    print('Testing:', linear_svm.score(test_data, test_label.ravel()))

    print('\n\n--------------SVM RBF Gamma 1------------------\n\n')
    rbf_svm = SVC(kernel='rbf', gamma=1)
    rbf_svm.fit(reduced_train_data, reduced_train_label.ravel())
    print('RBF Kernel (gamma=1) Accuracy:')
    print('Training:', rbf_svm.score(train_data, train_label.ravel()))
    print('Validation:', rbf_svm.score(validation_data, validation_label.ravel()))
    print('Testing:', rbf_svm.score(test_data, test_label.ravel()))
        
    print('\n\n--------------SVM RBF Gamma Auto------------------\n\n')
    rbf_svm = SVC(kernel='rbf', gamma='auto')
    rbf_svm.fit(reduced_train_data, reduced_train_label.ravel())
    print('RBF Kernel (gamma=auto) Accuracy:')
    print('Training:', rbf_svm.score(train_data, train_label.ravel()))
    print('Validation:', rbf_svm.score(validation_data, validation_label.ravel()))
    print('Testing:', rbf_svm.score(test_data, test_label.ravel()))

    print('\n\n--------------SVM RBF with Varying C------------------\n\n')
    # Values of C
    C = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # Initialize lists to store accuracies
    training_accuracies = []
    validation_accuracies = []
    testing_accuracies = []

    for c_value in C:
        rbf_svm = SVC(kernel='rbf', C=c_value, gamma='auto')
        rbf_svm.fit(reduced_train_data, reduced_train_label.ravel())

        # Append accuracies for current C value
        training_accuracies.append(rbf_svm.score(train_data, train_label.ravel()) * 100)
        validation_accuracies.append(rbf_svm.score(validation_data, validation_label.ravel()) * 100)
        testing_accuracies.append(rbf_svm.score(test_data, test_label.ravel()) * 100)

    # Plotting the accuracies
    plt.figure(figsize=(10, 6))
    plt.plot(C, training_accuracies, label='Training Accuracy', marker='o')
    plt.plot(C, validation_accuracies, label='Validation Accuracy', marker='o')
    plt.plot(C, testing_accuracies, label='Testing Accuracy', marker='o')

    plt.title('Accuracy vs C for SVM with RBF Kernel')
    plt.xlabel('C (Regularization Parameter)')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    print('\n\n--------------SVM RBF with best C------------------\n\n')
    rbf_model_full = svm.SVC(kernel = 'rbf', gamma = 'auto', C = 70)
    rbf_model_full.fit(train_data, train_label.ravel())

    print('----------\n RBF with FULL training set with best C : \n------------')
    print('\n Training Accuracy:' + str(100 * rbf_model_full.score(train_data, train_label)) + '%')
    print('\n Validation Accuracy:' + str(100 * rbf_model_full.score(validation_data, validation_label)) + '%')
    print('\n Testing Accuracy:' + str(100 * rbf_model_full.score(test_data, test_label)) + '%')
    """
    Script for Extra Credit Part
    """
    # FOR EXTRA CREDIT ONLY
    W_b = np.zeros((n_feature + 1, n_class))
    initialWeights_b = np.zeros((n_feature + 1, n_class))
    opts_b = {'maxiter': 100}
    
    args_b = (train_data, Y)
    nn_params = minimize(mlrObjFunction, initialWeights_b.flatten(), jac=True, args=args_b, method='CG', options=opts_b)
    W_b = nn_params.x.reshape((n_feature + 1, n_class))
    
    # Find the accuracy on Training Dataset
    predicted_label_b = mlrPredict(W_b, train_data)
    print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label_b == train_label).astype(float))) + '%')
    
    # Find the accuracy on Validation Dataset
    predicted_label_b = mlrPredict(W_b, validation_data)
    print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label_b == validation_label).astype(float))) + '%')
    
    # Find the accuracy on Testing Dataset
    predicted_label_b = mlrPredict(W_b, test_data)
    print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label_b == test_label).astype(float))) + '%')


    