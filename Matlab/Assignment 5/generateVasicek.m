function returnFunc = createVasicek(a,b,c,x,y,z,xs,ys,zs,h,t,s,muX,sigmaX)
    
    gamm=sigmaX*sqrt(1-exp(-2*a*h));
    density=(pi*gamm^2/a)^(-1/2)*exp(-(x-b-(xs-b)*exp(-a*h))^2*a/(gamm^2));
    
    tempFunc = subs(density,{a,b,c,h,xs},{1,1,2,1/52,1});
    returnFunc = simplify(tempFunc);
end
