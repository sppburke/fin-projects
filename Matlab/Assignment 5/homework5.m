function homework5()
    
    % Sean Burke
    % Econometrics 2
    % Homework 5

    % Clear all of the prior run's contents
    clc
    clear
    
    format ShortG;

    % Symbolic variables to create transition density
    syms a b c
    syms xs ys zs
    syms x y z
    syms h t s
    
    % Assign the mu and sigma as desired
    muVal= a * (b - x);
    sigmaVal = c;

    % Create the transition density
    createVasicekFunc = createVasicek(a,b,c,x,y,z,xs,ys,zs,h,t,s,muVal,sigmaVal);
    vasicekTransitionFunc = createTransitionFunc(a,b,c,x,y,z,xs,ys,zs,h,t,s,muVal,sigmaVal);

    % Set x values and both transition densities
    x = linspace(-2, 2, 50);
    createdFunc = ((137438953472.*52.^(1/2).*exp(-(13.*(x - 1).^2)/2).*((6167724.*x.^4)/2197 - (24670896.*x.^3)/2197 - (855302792.*x.^2)/28561 + (2352048880.*x)/28561 + 121860670536/371293))/253999128680651745);
    knownFunc = (exp((x - 1).^2/(4.*(exp(-1/26) - 1)))/(2.*pi.^(1/2).*(1 - exp(-1/26)).^(1/2)));

    % Graph created density
    figure;
    subplot(3, 1, 1)
    plot(x, createdFunc);
    title('Created Vasicek Transition Density');
    
    % Graph known density
    subplot(3,1,2)
    plot(x, knownFunc);
    title('Known Vasicek Transition Density');
    
    % Graph difference between created and known densities
    subplot(3, 1, 3)
    diff = createdFunc - knownFunc;
    plot(x, diff);
    title('Difference Between Created and Known');

    % Read weekly data from fedfunds file
    data=csvread('Fedfunds.csv', 6, 1, ['B7..B58']);

    a = 1;
    b = 2;
    c = 3;
    dataPeriod = 1 / 52;

    % Find MLE of the vasicek-style formula
    startingParams = [a, b, c]';
    minOptions = optimset('LargeScale','off','Display','iter');
    funcMin = @(var)(-liklihood(@Vasicek, data, var, dataPeriod));
    [mle, tempA, tempB, tempC, tempD, H] = fminunc(funcMin, startingParams, minOptions);
    disp(mle);

    % Compute the summary statistics for mle
    disp(H);
    covarianceH = inv(H);
    standdevH = sqrt(diag(covarianceH));
    standerr = standdevH/sqrt(length(data)-1);
    pVal = 2*(1-normcdf(abs(mle),0,standerr));
    
    % Display the summary statistics
    disp('Hessian Covariance');
    disp(covarianceH);
    disp('Hessian Standard Deviation');
    disp(standdevH);
    disp('Hessian Standard Error');
    disp(standerr);
    disp('Confidence Interval');
    [mle-(1.96*standerr) mle+(1.96*standerr)]
    disp('P-Value');
    disp(pVal);
    
end

function rtnLikli = liklihood(densityFunc, data, startingParams, dataPeriod)
% Return the minimum liklihood function

    tempLikli = 0;
    n = length(data);
    
    % Sum all outputs
    for i=2:n
        
        data1 = data(i);
        data2 = data(i-1);
        
        tempLikli =  tempLikli + log(densityFunc(data1, data2, startingParams,dataPeriod));
        
    end
    
    rtnLikli = tempLikli;
    
end