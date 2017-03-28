function [herm] = hermiteExpansion(k)
% Return the Hermite expansion

    syms z;
    tempH{1} = sym('1');
    
    for n=2:k
        tempH{n}=simplify(z*tempH{n-1}-diff(tempH{n-1},z));
    end
    
    herm=tempH{k};
end
