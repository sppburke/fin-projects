function rtnFunc = createTransitionFunc(a,b,c,x,y,z,xs,ys,zs,h,t,s,muX,sigmaX)
    syms HTemp Expectation Bt
    clear Bt HTemp Expectation
    K=5;
    J=K+1;
    fX2Y=int(1/sigmaX,x);
    fY2X=subs((finverse(fX2Y)),x,y);
    muY_temp=muX/sigmaX-sym('1')/sym('2')*diff(sigmaX,x,1);
    muY=subs(muY_temp,x,fY2X);
    muY=simplify(muY);
    sigmaY=sym('1');

    fY2Z=h^(-1/2)*(y-ys);
    fZ2Y=h^(1/2)*z+ys;


    for n=1:K
        HTemp=subs(Hermite(n),z,fY2Z);
        Expectation=HTemp;
        for k=1:J
            HTemp = muY*diff(HTemp,y,1)+sym('1')/sym('2')*diff(HTemp,y,2);
            Expectation=Expectation+h^k/factorial(k)*HTemp;
        end
        Bt{n}=sym('1')/factorial(n-1)*subs(Expectation,y,ys);
    end

    pZ=sym('0');
    for m=1:K
        pZ=pZ+Bt{m}*Hermite(m);
    end
    symvar(pZ);

    pZ=exp(-z^2/2)/sqrt(2*pi)*pZ;
    pY=(h^(-1/2))*subs(pZ,z,fY2Z);
    pX=(sigmaX^(-1))*subs(pY,y,fX2Y);
    pX=subs(pX,ys,subs(fX2Y,x,xs));
    pX=simplify(pX);
    rtnFunc=subs(pX,{a,b,c,h,xs},{1,1,2,1/52,1}); %VASICEK MODEL
    %g1=subs(pX,{a,b,c,h,xs},{1,1,2,1/250,param}); 
    %g1=pX;
end 

