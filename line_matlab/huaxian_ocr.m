im=imread('./OCR005.jpg');
im = im(918:1043, 256:1653, :);
% im = im(930:975, 256:1653, :);
% im = im(992:1039, 256:1653, :);
im_gray = rgb2gray(im);
% im = histeq(im);
% im = medfilt2(im, [5, 5]);
figure(1);
imshow(im_gray);

im = im2bw(im_gray, 0.9);
figure(2)
imshow(im);
texts = ocr(im);
texts.Text

[L,n]=bwlabel(im);
B = [0, 1, 0; 1, 1, 1; 0, 1, 0]; 
for i = 1:n
    im2 = L==i;
    im3 = imdilate(im2, B);
    im4 = imdilate(im3, B);
    im5 = imdilate(im4, B);
    im6 = imdilate(im5, B);
    if mean(im_gray(xor(im3, im6))) > 50
        im(L==i) = 0;
    end
end

texts = ocr(im);
texts.Text
re_pos1 = '(?<=\()[1-9]\d*.\d*|0\.\d*[1-9]\d*';
re_pos2 = '([1-9]\d*.\d*|0\.\d*[1-9]\d*)(?=,\n)';
re_pos3 = '(?<=D\s)([1-9]\d*.\d*|0\.\d*[1-9]\d*)(?=m)';
pos1 = regexp(texts.Text, re_pos1, 'match');
pos2 = regexp(texts.Text, re_pos2, 'match');
dist = regexp(texts.Text, re_pos3, 'match');
pos1(1)
pos2(1)
dist(1)