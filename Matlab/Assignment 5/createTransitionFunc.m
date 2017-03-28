function rtnFunc = createTransitionFunc(a,b,c,x,y,zFunc,xs,ys,zs,h,t,s,muVal,sigmaVal)
    
    % Create and clear variables
    syms HTemp Expectation Bt
    clear HTemp Expectation Bt
    
    % Assign variables
    K = 5;
    J = K + 1;
    
    % Calculate and assemble function
    fXtoY = int(1 / sigmaVal, x);
    fYtoX = subs((finverse(fXtoY)),x,y);
    tempMuVal = muVal / sigmaVal - sym('1') / sym('2') * diff(sigmaVal, x, 1);
    newMu = subs(tempMuVal, x, fYtoX);
    newMu = simplify(newMu);
    % newSigmaVal = sym('1');

    fYtoZ = h^(-1/2)*(y-ys);
    % fZtoY = h^(1/2)*z+ys;

    % Handle the formula expansion
    for n = 1:K
        
        HTemp = subs(hermiteExpansion(n),zFunc,fYtoZ);
        expectFunc = HTemp;
        
        for k= 1:J
            
            HTemp = newMu*diff(HTemp, y, 1) + sym('1') / sym('2') * diff(HTemp, y, 2);
            expectFunc = expectFunc + h^k / factorial(k) * HTemp;
            
        end
        
        Bt{n} = sym('1') / factorial(n - 1) * subs(expectFunc, y, ys);
        
    end

    % Create new formula
    pZ = sym('0');
    for m = 1:K
        pZ = pZ + Bt{m} * Hermite(m);
    end
    symvar(pZ);

    % Create the known func
    zFunc = exp(-zFunc^2 / 2) / sqrt(2 * pi) * pZ;
    yFunc = (h^(-1 / 2))*subs(pZ, zFunc, fYtoZ);
    xFunc = (sigmaVal^(-1)) * subs(yFunc, y, fXtoY);
    xFunc = subs(xFunc, ys, subs(fXtoY, x, xs));
    xFunc = simplify(xFunc);
    
    % Return the function
    rtnFunc = subs(xFunc,{a,b,c,h,xs},{1,1,2,1/52,1});
    
end 

