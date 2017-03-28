function homework3()

    % Sean Burke
    % Econometrics 2
    % Homework 3

    % Clear variables and terminal
    clc;
    clear

    % Format output to avoid scientific notation
    format shortG;

    % Full sample procedures
    % Input and find log returns
    tempAdjClose = xlsread('spdaily.xlsx', 'G:G');
    adjClose = flipud(tempAdjClose);
    tempReturns = diff(log(adjClose));
    returns = flipud(tempReturns);

    % Plot prices
    plot(adjClose);
    xlabel('Time');
    ylabel('Prices');
    title('Prices over Time');

    % Plot log returns
    figure;
    plot(returns);
    xlabel('Time');
    ylabel('Returns');
    title('Returns over Time');

    % Plot ACF for returns
    figure;
    autocorr(returns)
    title('ACF for Returns');

    % Plot PACF for returns
    figure;
    parcorr(returns);
    title('PACF for Returns');

    % Plot ACF for squared returns
    figure;
    autocorr(returns.^2);
    title('ACF for Squared Returns');

    % Conduct tests
    [H, pValue, Stat, CriticalValue] = lbqtest(returns-mean(returns), [10 15 20]', .05);
    [H, pValue, Stat, CriticalValue];

    [H, pValue, Stat, CriticalValue] = lbqtest((returns-mean(returns)).^2, [10 15 20]', .05);
    [H, pValue, Stat, CriticalValue];

    [H, pValue, Stat, CriticalValue] = archtest((returns-mean(returns)), [10 15 20]', .05);
    [H, pValue, Stat, CriticalValue];

    Mdl = arima('ARLags', 1, 'Variance', garch(1,1));
    estMdl = estimate(Mdl, returns);
    estMdl

    % Find and plot residuals
    [residual,var,logL] = infer(estMdl,returns);

    figure;
    subplot(3,1,2)
    plot(var)
    xlim([0,1256])
    title('Conditional Variance')
    subplot(3,1,1)
    plot(residual)
    xlim([0,1256])
    title('Residuals')
    subplot(3,1,3)
    plot(returns)
    xlim([0,1256])
    title('Returns')

    % Standardize residuals
    stres = residual./(var.^.5);

    % Plot standardized residuals
    figure;
    plot(stres);
    ylabel('Residuals')
    title('Standardized Residuals')

    % ACF for stanardized residuals
    figure;
    autocorr(residual)
    title('ACF for Standardized Residuals')

    % Compare stats to pre-estimation analysis
    [H, pValue, Stat, CriticalValue] = lbqtest((stres).^2,[10 15 20]',0.05);
    [H, pValue, Stat, CriticalValue];

    [H, pValue, Stat, CriticalValue] = archtest(stres,[10 15 20]',0.05);
    [H, pValue, Stat, CriticalValue];

    % Forecast volatility
    xaxis=[1:1257].';
    vF = forecast(estMdl,10,'Y0',returns);
    v = infer(estMdl,returns);

    % Plot forecasted volatility
    figure;
    plot(xaxis,v,'k:','LineWidth',2);
    hold on;
    plot(xaxis(end):xaxis(end) + 10,[v(end);vF],'r','LineWidth',2);
    title('Forecasted Conditional Variances of Nominal Returns');
    ylabel('Conditional variances');
    xlabel('Year');
    legend({'Estimation sample cond. var.','Forecasted cond. var.'},...
        'Location','Best');

    % Sub-sample procedures
    % Input and find log returns
    tempAdjClose = xlsread('spdaily_sub.xlsx', 'G:G');
    adjClose = flipud(tempAdjClose);
    tempReturns = diff(log(adjClose));
    returns = flipud(tempReturns);

    % Display model
    Mdl = arima('ARLags', 1, 'Variance', garch(1,1));
    estMdl = estimate(Mdl, returns);
    estMdl

end
