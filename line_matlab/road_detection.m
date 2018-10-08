% 
% %% Hough transform
% im=imread('./test.png');
% I  = rgb2gray(im); % convert to intensity
% BW=I;
% thresh=[0.01,0.17];
% sigma=2;%定义高斯参数
% f = edge(double(BW),'canny',thresh,sigma);
% figure(1),imshow(f,[]);title('canny 边缘检测');
% % [H, theta, rho]= hough(f, 'RhoResolution', 0.5);
% [H, theta, rho]= hough(f);
% %imshow(theta,rho,H,[],'notruesize'),
% axis on,
% axis normal
% %xlabel('\theta'),ylabel('rho');
% peaks=houghpeaks(H,5);
% hold on
% lines=houghlines(f,theta,rho,peaks);
% figure,imshow(f,[]),title('Hough Transform Detect Result'),
% hold on
% for k=1:length(lines) 
%     xy=[lines(k).point1;lines(k).point2];
% plot(xy(:,1),xy(:,2),'LineWidth',4,'Color',[.6 .6 .6]);
% end
% 
% 
% %%
% %Lab space, smooth image patch
% path_road = './road.png';
% path_water = './water.png';
% path_whole = './test.png';
% road=imread(path_whole);
% patch_size = 1;
% ker = fspecial('average', patch_size);
% lab_road = rgb2lab(road);
% ab=lab_road(:,:,2:3);
% ab(:,:,1) = filter2( ker, ab(:,:,1));
% ab(:,:,2) = filter2( ker, ab(:,:,2));
% ab=reshape(ab,[size(ab,1)*size(ab,2),size(ab,3)]);
% figure;
% h = histogram2(ab(:,1), ab(:,2), [-128:127], [-128:127]);
% % heatmap from the histogram
% counts = h.Values;
% G = counts/max(counts(:)); % Or whatever you did.
% heatMap = imresize(G, [500, 500]);
% imshow(heatMap, [], 'XData', h.XBinEdges, 'YData', h.YBinEdges);
% axis on;
% colormap(hot(256));
% colorbar;
% 
% 
% %%
% %YCbCr space
% path_road = './road.png';
% path_water = './water.png';
% path_whole = './test.png';
% im=imread(path_road);
% patch_size = 1;
% ker = fspecial('average', patch_size);
% ycbcr = rgb2ycbcr(im);
% cbcr=ycbcr(:,:,2:3);
% cbcr(:,:,1) = filter2( ker, cbcr(:,:,1));
% cbcr(:,:,2) = filter2( ker, cbcr(:,:,2));
% cbcr=reshape(cbcr,[size(cbcr,1)*size(cbcr,2),size(cbcr,3)]);
% figure;
% h = histogram2(cbcr(:,1), cbcr(:,2), [0:255], [0:255]);
% % heatmap from the histogram
% counts = h.Values;
% G = counts/max(counts(:)); % Or whatever you did.
% heatMap = imresize(G, [500, 500]);
% imshow(heatMap, [], 'XData', h.XBinEdges, 'YData', h.YBinEdges);
% axis on;
% colormap(hot(256));
% colorbar;
% 
% 
% %%
% %HSL space 
% path_road = './road.png';
% path_water = './water.png';
% path_whole = './test.png';
% im=imread(path_water);
% patch_size = 1;
% ker = fspecial('average', patch_size);
% hsl = rgb2hsi(im);
% hs=hsl(:,:,1:2);
% hs(:,:,1) = filter2( ker, hs(:,:,1));
% hs(:,:,2) = filter2( ker, hs(:,:,2));
% hs=reshape(hs,[size(hs,1)*size(hs,2),size(hs,3)]);
% figure;
% h = histogram2(hs(:,1), hs(:,2), [0:1/360:1], [0:1/100:1]);
% % heatmap from the histogram
% counts = h.Values;
% G = counts/max(counts(:)); % Or whatever you did.
% heatMap = imresize(G, [500, 500]);
% imshow(heatMap, [], 'XData', h.XBinEdges, 'YData', h.YBinEdges);
% axis on;
% colormap(hot(256));
% colorbar;


%% test
% th_lab_water = -[13.04, 14.06; -20.17, -19.15];
th_lab_water = [-16, -10; 17, 22];
th_lab_road = [-9.954, -6.888; -3.822, -0.7555];
% th_ycbcr_water = [116, 117; 120.1, 121.1];
% th_ycbcr_water = [-118, -116; -122, -120];
th_ycbcr_water = [115, 118; 119, 122];
% th_ycbcr_road = [119.1, 124.2; 134.9, 138.5];
th_ycbcr_road = [119, 125; 134, 139];
% th_hsl_road = [0.05812, 0.1082; 0.5691, 0.5932];
th_hsl_road = [0.057, 0.11; 0.56, 0.60];
% th_hsl_water = [0.2164, 0.2725; 0.3487, 0.3547];
th_hsl_water = [0.21, 0.28; 0.33, 0.36];
path_road = './road.png';
path_water = './water.png';
path_whole = './test.png';
im = imread(path_whole);

% test Lab on the whole image
th = th_hsl_road;
% th = th_lab_water;
patch_size = 1;
% cspace = rgb2lab(im);
% cspace = rgb2ycbcr(im);
cspace = rgb2hsi(im);
ker = fspecial('average', patch_size);
ab=cspace(:,:,1:2);
ab(:,:,1) = filter2( ker, ab(:,:,1));
ab(:,:,2) = filter2( ker, ab(:,:,2));
ind = zeros(size(ab,1), size(ab,2));
ind(ab(:,:,1)>=th(1,1) & ab(:,:,1)<=th(1,2) & ab(:,:,2)>=th(2,1) & ab(:,:,1)<=th(2,2)) = 1;
imshow(ind);


%% superpixel
path_road = './road.png';
path_water = './water.png';
path_whole = './test.png';
path_whole = './788.jpg';
im = imread(path_whole);
im = imresize(im, 0.25);
im_lab = rgb2ycbcr(im);
N = 400;

[L,NumLabels] = superpixels(im_lab, N, 'Compactness', 20, 'IsInputLab', false);
BW = boundarymask(L);
imshow(imoverlay(im,BW,'cyan'),'InitialMagnification',67);
