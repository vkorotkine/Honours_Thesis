import autograd.numpy as np
import autograd.numpy.random as npr
from autograd.extend import primitive, defvjp

from scipy.optimize import minimize
from autograd import grad
from autograd.misc import flatten
from autograd.wrap_util import wraps
from autograd.misc.optimizers import adam, sgd
from matplotlib import pyplot as plt

from scipy.optimize import basinhopping

@primitive
def relu(x):
  return x * (x > 0)

def relu_vjp(ans, x):
  return lambda x:(x>0).astype(float)

defvjp(relu, relu_vjp)

def init_random_params(scale, layer_sizes, rs=npr.RandomState()):
    """Build a list of (weights, biases) tuples,
       one for each layer in the net."""
    return [[scale * rs.randn(m, n),   # weight matrix
             scale * rs.randn(n)]      # bias vector
            for m, n in zip(layer_sizes[:-1], layer_sizes[1:])]
    
def init_ones_params(scale, layer_sizes, rs=npr.RandomState()):
    """Build a list of (weights, biases) tuples,
       one for each layer in the net."""
    return [[scale * np.ones(m, n),   # weight matrix
             scale * np.ones(n)]      # bias vector
            for m, n in zip(layer_sizes[:-1], layer_sizes[1:])]


def neural_net_predict(params, inputs):
    for W, b in params:
        outputs = np.dot(inputs, W) + b
        inputs=np.tanh(outputs)
        #inputs=relu(outputs);
        #inputs = sigmoid(outputs);
    return outputs 

def dtanh_dx(x):
    return 1.-np.square(np.tanh(x))

def neural_net_derivative(params, inputs):
    #For a neural network with one output
    #Compute gradient of network w.r.t inputs
    for i, (W, b) in enumerate(params):
        if i==0:
            outputs = np.dot(inputs, W) + b
            inputs=np.tanh(outputs)
        else: 
            outputs = np.dot(inputs, W) + b
            inputs=np.tanh(outputs)
        #inputs=relu(outputs);
        #inputs = sigmoid(outputs);
    return outputs 




def my_unflatten_optimizer(optimize):
    """Takes an optimizer that operates on flat 1D numpy arrays and returns a
    wrapped version that handles trees of nested containers (lists/tuples/dicts)
    with arrays/scalars at the leaves."""
    @wraps(optimize)
    def _optimize(fun, grad, x0, callback=None, *args, **kwargs):
        _x0, unflatten = flatten(x0)
        _fun = lambda x: flatten(fun(unflatten(x)))[0]
        _grad = lambda x: flatten(grad(unflatten(x)))[0]
        
        if callback:
            _callback = lambda x: callback(unflatten(x))
        else:
            _callback = None
        result=optimize(_fun, _grad, _x0, _callback, *args, **kwargs)
        return unflatten(result.x), result.fun
        #return unflatten(optimize(_fun, _grad, _x0, _callback, *argss, **kwargs))

    return _optimize



@my_unflatten_optimizer
def unflattened_lbfgs(fun, grad, x, callback, max_feval, max_iter):    
    ret=minimize(fun, x, method='L-BFGS-B', jac=grad, callback=callback, options={'disp': True,'maxIter':max_iter, 'maxfun':max_feval} )#, hess=None, hessp=None, bounds=None, constraints=(), tol=None, callback=None, options=None)
    return ret


def get_parameters(loss_function, layer_sizes, max_iter,max_funeval):
    """
    Optimizes loss_function(params) over neural net parameters defined by layer_sizes. 
    """

    p0=init_random_params(1, layer_sizes)
    
    p, _=unflattened_lbfgs(loss_function, grad(loss_function,0),p0,\
        max_feval=max_funeval, max_iter=max_iter, callback=None)
    return p;