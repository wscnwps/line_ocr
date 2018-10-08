function [output] = hsv2hsl(input)
if (numel(input)==3)
    input=reshape(input,1,3);
elseif ((size(input,2)~=3)||(ndims(input)~=2))
    error('myApp:argChk','Input error. Matrix dimensions do not fit.');
end
if ((min(min(input))<0)||(max(max(input))>1)) 
    error('myApp:argChk','Input error. Matrix elements out of range');
else    
    output=zeros(size(input));
    for j=1:size(input,1);
    if((2-input(j,2))*input(j,3)<=1)
       output(j,2)=input(j,2)*input(j,3)/((2-input(j,2))*input(j,3));
    else
        output(j,2)=input(j,2)*input(j,3)/(2-(2-input(j,2))*input(j,3));
    end
    output(j,3)=(2-input(j,2))*input(j,3)/2;
    output(j,1)=input(j,1); 
    end
end
