function homework2()

% Sean Burke
% Econometrics 2
% Homework 2

% Clear the terminal and output variables
clc; 
clear; 

% Define the mu and sigma array
mu = [2 5];
sigma = [0.05 0; 0 0.1];

% Acquire input for number of random variables
num = input('Input number of random variables: ');
conf = input('Input confidence level as decimal (i.e. .95): ');

% Get array of random variables based on inputs
randnum = mvnrnd(mu, sigma, num);

% Optimize the function to find theta and theta
pfunc = @(x, var) (1 / (2 * pi * sqrt(det(sigma)))) * exp(-0.5 * (x-var) * sigma * transpose(x - var));
[theta, ltheta] = mfunc(@(var) likelifunc(randnum, pfunc, var));

% Print out Theta and L-Theta
disp('Theta');
disp(theta);
disp('L-Theta');
disp(ltheta);

% Calcuate and print Confidence Intervals and P-Values
% First row
getCI(randnum(:, 1), conf, num);
getPVal(randnum, mean(randnum(:, 1)), num);

% Second row
getCI(randnum(:, 2), conf, num);
getPVal(randnum, mean(randnum(:, 2)), num);

end

function likelirtn = likelifunc(randnum, pdfunc, var)

    % Calculate likelihood
    likelirtn = 0;
    for count = 1:length(randnum)
        likelirtn = likelirtn + log(pdfunc(randnum(count,:), var));
    end

end

function [theta, ltheta] = mfunc(func)

% Calculate theta and ltheta
theta = fminsearch(@(x) func(x) * - 1, [1, 2]);
ltheta = func(theta);

end

function getCI(randnum, conf, num)

% Calculate confidence interval
meannum = mean(randnum);
stddev = std(randnum);
critval = tinv(conf, num - 1);
confinter = (critval * stddev) / sqrt(num);

% Print confidence invterval
disp('Confidence Interval');
disp('Lower Bound');
disp(meannum - confinter);
disp('Upper Bound');
disp(meannum + confinter);

end

function getPVal(randnum_all, mu, num)

% Caclulate p-value
meannum = mean(randnum_all);  
stddev = std(randnum_all);      
tval = (meannum - mu) / (stddev / sqrt(num));
pval = 2 * (1 - tcdf(abs(tval), num - 1));

% Print p-value
disp('P-Value');
disp(pval);

end 
