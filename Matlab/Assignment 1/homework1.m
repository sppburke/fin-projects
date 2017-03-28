function homework1()

% Sean Burke
% Econometrics 2
% Homework 1

% Clear the terminal and output variables
clc; 
clear; 

% Create an array of random variable data based on normal distribution
sigma = .1;
rndnum = getRandomNums(sigma);

% Create the PDF and corresponding likelihood function
pdfunc = @(x,mu,)(1/(sqrt(2*pi)*0.1)).*exp(-1*((x-mu).^2)/((2*0.1).^2));
lhfunc = @(var)sum(log(pdfunc(rndnum, var)));

% Create the maximization function
theta = fminsearch(@(x)-lhfunc(x),0);
ltheta = lhfunc(theta);

% Obtain the confidence interval and p-value
[h,pval,confin] = ttest(rndnum,theta);

% Print the relevant values
printValues(theta,ltheta,confin,pval);

end

function nums = getRandomNums(s) 

n = input('Number of random points: ');
nums = random('Normal', 0, s, [n, 1]);

end

function printValues(t, lt, c, p)

disp('Theta');
disp(t);
disp('LTheta');
disp(lt);
disp('Confidence Interval (95%)');
disp(c);
disp('P-value');
disp(p);

end
