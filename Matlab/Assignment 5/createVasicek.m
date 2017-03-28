function returnFunc = createVasicek(a,b,c,x,y,z,xs,ys,zs,h,t,s,muX,sigmaX)
% Return the created vasicek density

    gammaVal = sigmaX * sqrt(1 - exp(-2 * a * h));
    densityFunc = (pi * gammaVal^2 / a)^(-1 / 2)*exp(-(x - b -(xs - b)*exp(-a * h))^2 * a /(gammaVal^2));
    
    tempFunc = subs(densityFunc,{a,b,c,h,xs},{1,1,2,1/52,1});
    returnFunc = simplify(tempFunc);
end
