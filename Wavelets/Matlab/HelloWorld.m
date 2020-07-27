%{
* The signal is represented in the time domain.
* The Fourier transform has the drawback of dealing with just the
frequency component in the signal. (the temporary details are not
available)
* Wavelets solves this problem, by concentrating in time as well in
frequency domain around a certain point.
* We can have
    1). high frequency resolution and poor time resolution
    2). poor frequency resolution and good time resolution
* So, using wavelets we can get
    1). good frequency resolution for low frequency components
    2). good time resolution for high frequency components
* Types of mother wavelets
    - Haar
    - Daubechies
    - Morlet

* Steps for decomposition
1). For the original image
    1.1). Apply low pass filter to preserve low frequencies on the rows
        * The subsignal produced will have the highest frequency equal to
        half of the original. 
        (According to Nyquist sampling theory, this change in frequency
        range means that only half of original samples need to be kept in
        order to perfectly reconstruct the signal)
    1.2). Apply high pass filter to preserve high frequencies on the rows
2). We get 2 representations. For each, we subsample it by two and then we 
apply the same principle
    2.1). On the low pass filtered
        2.1.1). Low pass   => Aproximate Image  (LL)
        2.1.2). High pass  => Vertical Detail   (LH)
    2.2). On the high pass filtered
        2.2.1). Low pass   => Horizontal Detail (HL)
        2.2.2). High pass  => Diagonal Detail   (HH)n 

* Matlab functions
    [CAprox, CHoriz, CVerti, CDiag] = dwt2(image, 'wavelet_type')
%}


% read the image
image = imread('lena.png');
figure;
imshow(image);

% apply the Daubechies wavelet on each channel of the image (r,g,b)
[xar, xhr, xvr, xdr] = dwt2(image(:,:,1), 'db2');
[xag, xhg, xvg, xdg] = dwt2(image(:,:,2), 'db2');
[xab, xhb, xvb, xdb] = dwt2(image(:,:,3), 'db2');


% compose the results for each channel to compose the 4 subdomains
xa(:,:,1) = xar;    xh(:,:,1) = xhr;    xv(:,:,1) = xvr;    xd(:,:,1) = xdr;
xa(:,:,2) = xag;    xh(:,:,2) = xhg;    xv(:,:,2) = xvg;    xd(:,:,2) = xdg;
xa(:,:,3) = xab;    xh(:,:,3) = xhb;    xv(:,:,3) = xvb;    xd(:,:,3) = xdb;

% plot the result
%figure; imshow(xa/255);
%figure; imshow(xh);
%figure; imshow(xv);
%figure; imshow(xd);

X1 = [xa * 0.003 log10(xv)* 0.3; log10(xh) * 0.3 log10(xd) * 0.3];
figure; imshow(X1);





