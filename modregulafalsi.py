""" **modregulafalsi.py**
    
    This script performs the modified regula falsi method.

"""

from __future__ import print_function
import logging
from random import random

tolerance = 0.05    # Change this to be your preferred tolerance
resolution = 0.0    # The resolution of the axis being searched


def modregulafalsi(func, a0, b0, *args, **kwargs):
    """Find the root of func using t0 and t1 as guesses.
    
    Parameters
    ----------
    func : callable
        A one-dimensional continuous function to be
        evaluated for its root.
    a0 : float
        Low initial guess. Should result in the opposite
        sign of a0 after evaluation.
    b0 : float
        High initial guess. Should result in the opposite
        sign of t0 after evaluation.
    args : list, optional
        Arguments for func.
    kwargs : dict, optional
        Key word arguments for func.
        
    Returns
    -------
    troot : float
        The root of func.
    """
    # First prepare the guesses
    funcinput = prepareinput(func, a0, b0, *args, **kwargs)

    # Assign values
    try:
        a0, b0 = funcinput
    except TypeError:
        # If one value was returned, its a root
        return funcinput

    # Set up class object
    falsifunc = FalsiFunction(func, *args, **kwargs)

    # Initial conditions:
    k = 0
    ak, bk, fck1 = a0, b0, -1
    ck = falsifunc.newx_regfalsi(ak, bk)

    # Keep searching until the function is close enough to 0:
    while not (0.0 <= falsifunc.evaluate(ck) < tolerance):
        k += 1

        # Reset alpha and beta
        alpha, beta = 1, 1

        # Evaluate the function at low value and new value
        fak = falsifunc.evaluate(ak)
        fck = falsifunc.evaluate(ck)
        logging.debug('k = {0}:\n  [a{0}, b{0}] = [{1:2.1f},  '
                      '{2:2.1f}]\n  c{0} = {3:4.2f}: f(c{0}) ~ {4:6.2f}'.
                      format(k - 1, ak, bk, ck, fck))

        # If the difference between ak and ck is smaller than
        # resolution, return the positive value
        if abs(ak - ck) <= resolution:
            return ak if fak >= 0 else ck

        # If root is between ak and ck:
        if (fak * fck) <= 0:
            # If ck is the root, return position:
            if fck == 0:
                return ck
            # Else, set upper end at ck
            bk = ck
            # Update alpha
            if k > 1 and (fck * fck1) > 0:
                alpha = 0.5

        # If root is between ck and bk:
        else:
            # Set lower end at ck
            ak = ck
            # Update beta
            if k > 1 and (fck * fck1) > 0:
                beta = 0.5
        fck1 = fck
        ck = falsifunc.newx_modregfalsi(ak, bk, alpha, beta)

    # Return root
    return ck


class FalsiFunction:
    def __init__(self, func, *args, **kwargs):
        """Class to perform evaluations of func.
        
        Parameters
        ----------
        func : callable
            A one-dimensional continuous function to be
            evaluated for its root.
        args : list
            Arguments for func.
        kwargs : dict
            Key word arguments for func.
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def evaluate(self, c):
        """Evaluate self.func at point c."""
        f = self.func(c, *self.args, **self.kwargs)
        return f

    def newx_regfalsi(self, ak, bk):
        """Return a new position via the regula falsi method."""
        fa = self.func(ak, *self.args, **self.kwargs)
        fb = self.func(bk, *self.args, **self.kwargs)
        ck = (ak * fb - bk * fa) / (fb - fa)
        return ck

    def newx_modregfalsi(self, ak, bk, alpha, beta):
        """Return a new position via modified regula falsi method."""
        fa = self.func(ak, *self.args, **self.kwargs)
        fb = self.func(bk, *self.args, **self.kwargs)
        ck = (ak * beta * fb - bk * alpha * fa) / (beta * fb - alpha * fa)
        return ck


def prepareinput(func, a0, b0, *args, **kwargs):
    """This function checks that initial guesses will yield 
    f(a0)f(b0) < 0.
    
    Parameters
    ----------
    func : callable
        A one-dimensional continuous function to be
        evaluated for its root.
    a0 : float
        Low initial guess. Should result in the opposite
        sign of a0 after evaluation.
    b0 : float
        High initial guess. Should result in the opposite
        sign of t0 after evaluation.
    args : list
        Arguments for func.
    kwargs : dict
        Key word arguments for func.
        
    Returns
    -------
    a0 : float
        Useful low initial guess.
    b0 : float
        Useful high initial guess.
    """
    # Evaluate guesses
    fa = func(a0, *args, **kwargs)
    fb = func(b0, *args, **kwargs)
    negcheck = fa * fb

    # If one of the values is a root, return that value
    if fa == 0:
        logging.info('Your initial guess {0:4.2f} is a root.'.format(a0))
        return a0
    elif fb == 0:
        logging.info('Your initial guess {0:4.2f} is a root.'.format(b0))
        return b0
    # If passes test, return both values
    elif negcheck < 0:
        return a0, b0
    else:
        # Find new initial guesses
        return findnewinput(func, a0, b0, *args, **kwargs)


def findnewinput(func, a0, b0, *args, **kwargs):
    """This function returns a0 and b0, the initial input for
    the regula falsi method.
    
    Parameters
    ----------
    func : callable
        A one-dimensional continuous function to be
        evaluated for its root.
    a0 : float
        Low initial guess. Should result in the opposite
        sign of a0 after evaluation.
    b0 : float
        High initial guess. Should result in the opposite
        sign of t0 after evaluation.
    args : list
        Arguments for func.
    kwargs : dict
        Key word arguments for func.
        
    Returns
    -------
    a0 : float
        Useful low initial guess.
    b0 : float
        Useful high initial guess.
    """
    # Evaluate func at original guesses
    fa = func(a0, *args, **kwargs)
    fb = func(b0, *args, **kwargs)

    # 'for' instead of 'while' to avoid infinite loop
    for k in range(1000):
        # Find new guess
        c0 = newguessbydecay(func, a0, b0, *args, **kwargs)
        # If new guess is below range, shift down
        if c0 < a0:
            a0, b0 = c0, a0
        # If new guess is above range, shift up
        elif c0 > b0:
            a0, b0 = b0, c0
        # If new guess is within range, check for signage
        else:
            fc = func(c0, *args, **kwargs)
            # If c is a root, return c by itself
            if fc == 0:
                return c0
            elif fa * fc < 0:
                return a0, c0
            elif fc * fb < 0:
                return c0, b0
            else:
                rannum = random()
                if rannum < 0.5:
                    a0 = c0
                else:
                    b0 = c0

        # Evaluate func at new guesses
        fa = func(a0, *args, **kwargs)
        fb = func(b0, *args, **kwargs)

        # Return if factor is negative
        if fa * fb < 0:
            return a0, b0
    return a0, b0


def newguessbydecay(func, a, b, *args, **kwargs):
    """This function returns new guesses for func that will
    hopefully have the opposite sign of a0 and b0. This
    module assumes a decaying function.
    
    Parameters
    ----------
    func : callable
        A one-dimensional continuous function to be
        evaluated for its root.
    a : float
        Low initial guess. Should result in the opposite
        sign of a0 after evaluation.
    b : float
        High initial guess. Should result in the opposite
        sign of t0 after evaluation.
    args : list
        Arguments for func.
    kwargs : dict
        Key word arguments for func.
        
    Returns
    -------
    c : float
        New guess.
    """
    # Evaluate func at original guesses
    fa = func(a, *args, **kwargs)
    fb = func(b, *args, **kwargs)
    slope = (fb - fa) / (b - a)

    # If the current evaluations are negative, make y positive
    if fa < 0:
        # If slope is negative, positive value on left side
        if slope < 0:
            y = abs(fb)
        # If slope is positive, positive value on right side
        else:
            y = 2 * abs(fb)
    # If they're positive, make y negative
    else:
        # If slope is negative, negative value on right side
        if slope < 0:
            y = -2 * abs(fb)
        # If slope is positive, negative value on left side
        else:
            y = -1 * abs(fb)
    c = (y - fa) / slope + a
    return c


if __name__ == '__main__':

    def example(t):
        """Example function: cubic curve"""
        f = t ** 3 + t - 1
        return f

    logging.basicConfig(level=logging.DEBUG)
    troot = modregulafalsi(example, 0.0, 1.0)

    print('You have a root at t={0}.'.format(troot))
