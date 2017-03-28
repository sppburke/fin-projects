    function homework4()

    % Sean Burke
    % Econometics 2
    % Homework 4
    
    % load FTSE100 data
    format shortG;
    alphaSig = .05;
    adjClose = xlsread('spdaily.xlsx','G:G');
    returns = flipud(diff(log(flipud(adjClose))));
    
    % Use MLE to get thetaHat parameters
    thetaHat = findMLE(returns);
    rtnVars = num2cell(thetaHat);
    alpha0 = rtnVars{1}; % Alpha0
    alpha1 = rtnVars{2}; % Alpha1
    beta = rtnVars{3}; % Beta 
    
    % Use thetaHat parameters to simulate @ 500 periods
    thetaCount = 500; % Number of simulations to run
    completeArr = thetaCount:4;
    for index = 1:thetaCount
        
        [V,Y] = dataSimulator(thetaHat);
        newThetaHat = findMLE(Y);
        
        rtnVals = num2cell(newThetaHat);
        completeArr(index,2) = rtnVals{1}; % 2 = Alpha0
        completeArr(index,3) = rtnVals{2}; % 3 = Alpha1
        completeArr(index,4) = rtnVals{3}; % 4 = Beta 
        
    end
    
    % Find the p-value for all parameter distribution
    disp('Alpha0');
    disp(alpha0);
    generatePVal(completeArr(:, 2), alpha0, length(completeArr(:, 2))); % Alpha0
    
    disp('Alpha1');
    disp(alpha1);
    generatePVal(completeArr(:, 3), alpha1, length(completeArr(:, 3))); % Alpha1
    
    disp('Beta');
    disp(beta);
    generatePVal(completeArr(:, 4), beta, length(completeArr(:, 4))); % Beta
    
    % Find the confidence interval for all parameters
    [Low_A0, High_A0] = generateConfidenceInterval(completeArr(:, 2), alphaSig, length(completeArr(:, 2))); % Alpha0
    disp('Alpha0 Confidence Interval:');
    disp([Low_A0, High_A0]);
    
    [Low_A1, High_A1] = generateConfidenceInterval(completeArr(:, 3), alphaSig, length(completeArr(:, 3))); % Alpha1
    disp('Alpha1 Confidence Interval:');
    disp([Low_A1, High_A1]);
    
    [Low_B, High_B] = generateConfidenceInterval(completeArr(:, 4), alphaSig, length(completeArr(:, 4))); % Beta
    disp('Beta Confidence Interval:');
    disp([Low_B, High_B]);
    
    % Count each parameter within interval
    a0_counter = 0;
    a1_counter = 0;
    b_counter = 0;
    
    for index2 = 1:thetaCount
        
        %fprintf('\nSimulation number: %.f\n', index2)    
        
        % Alpha0
        newAlpha0 = completeArr(index2, 2);
        if and((newAlpha0 >= Low_A0),(newAlpha0 <= High_A0))
            a0_counter = a0_counter + 1;
        end
        
        % Alpha1
        newAlpha1 = completeArr(index2, 3);
        if and((newAlpha1 >= Low_A1),(newAlpha1 <= High_A1))
            a1_counter = a1_counter + 1;
        end
        
        % Beta
        newBeta= completeArr(index2, 4);
        if and((newBeta >= Low_B),(newBeta <= High_B))
            b_counter = b_counter + 1;
        end
        
    end
    
    % Display parameter counters
    disp('Alpha0 within range');
    disp(a0_counter);
    disp('Alpha1 within range');
    disp(a1_counter);
    disp('Beta within range');
    disp(b_counter);
    
    % Display acceptance rates
    disp('Total alpha0 acceptance rate') 
    disp(double(a0_counter) / double(thetaCount));
    disp('Total alpha1 acceptance rate') 
    disp(double(a1_counter) / double(thetaCount));
    disp('Total beta acceptance rate')
    disp(double(b_counter) / double(thetaCount));
    
end

function thetaHat = findMLE(returns)

    thetaSeed=[0.01,0.1,0.1]; % initial guess
    
    % Set the log liklihood maximization function
    logL=@(resi,vari)-sum(resi.^2 ./vari+log(2*pi*vari))/2;
    thetaHat = fminsearch(@(theta)-logL(returns,GARCH(returns,theta)),thetaSeed);
    
end

function [V,Y] = dataSimulator(coefficients)

    % Separate variables
    rtnVars = num2cell(coefficients);
    alpha0 = rtnVars{1};
    alpha1 = rtnVars{2};
    beta = rtnVars{3};
    
    % Assign variables to new arch/garch model
    Mdl = garch('Constant',alpha0,'GARCH',beta,'ARCH',alpha1);
    
    % Simulate with new arch/garch model
    [V,Y] = simulate(Mdl,1500);
    
end

function vari = GARCH(resi,theta)

    % Evaluate the GARCH timeseries model
    % Parameters: 'theta=[alpha0 alpha1 beta1]'
    % Assumes that 'resi(1)' is the oldest
    vari=nan(size(resi));
    if min([theta(1) - theta(2) - theta(3)]) > 0
        vari(1)=var(resi);
        for i=2:length(vari)
            vari(i)=theta(1)+theta(3)*vari(i-1)+theta(2)*resi(i-1)^2;
        end
    end
end

function generatePVal(data,mu,n)
    
    x = mean(data);
    s = std(data);
    t = (x - mu)/(s/sqrt(n));
    
    % Print t- and p- values
    fprintf('t-value = %.5f\n',t);
    p = 2*(1-tcdf(abs(t),n-1));
    fprintf('p-value = %.5f\n',p);
    
end 

function [L, H] = generateConfidenceInterval(data,alpha,n)

    x = mean(data);
    s = std(data);
    
    t_crit = tinv(1-(alpha/2), n-1);
    ci = (t_crit*s);
    L = x - ci;
    H = x + ci;
    
end