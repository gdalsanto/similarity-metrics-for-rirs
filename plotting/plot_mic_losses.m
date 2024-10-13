clear all; close all; clc
% for plots 
set(groot, 'defaulttextinterpreter','latex');  
set(groot, 'defaultAxesTickLabelInterpreter','latex');  
set(groot, 'defaultLegendInterpreter','latex');

addpath("./Colormaps")
mycolormap = customcolormap([0 .25 .5 .75 1], {'#9d0142','#f66e45','#ffffbb','#65c0ae','#5e4f9f'});

mrstft = load("../data/dict_mic_mrstft.mat");
power = load("../data/dict_mic_power.mat");
edc = load("../data/dict_mic_edc.mat");
esr = load("../data/dict_mic_esr.mat");

mrstft_loss = cell2mat(mrstft.dict_mrstft);
power_loss = cell2mat(power.dict_power);
edc_loss = cell2mat(edc.dict_edc);
esr_loss = cell2mat(esr.dict_esr);
%% 

load('../data/means.mat')
load('../data/stds.mat')
mrstft_loss = (mrstft_loss - means(1))/stds(1);
power_loss = (power_loss - means(2))/stds(2);
edc_loss = (edc_loss - means(3))/stds(3);
esr_loss = (esr_loss - means(4))/stds(4);

% generate sets of divisions
n_mics = 5; 
div = 1:n_mics;

med_power = zeros(n_mics, n_mics);
std_power = zeros(n_mics, n_mics);

for i = 1:length(div)
    for j = 1:length(div)
        % remove trailing zeros 
        last_nonzero = find(squeeze(power_loss(i,j,:)), 1,'last'); 
        data = squeeze(power_loss(i, j, 1:last_nonzero));
        med_power(i, j) = median(data); 
        std_power(i, j) = std(data);
    end
end

med_mrstft = zeros(n_mics, n_mics);
std_mrstft = zeros(n_mics, n_mics);

for i = 1:length(div)
    for j = 1:length(div)
        % remove trailing zeros 
        last_nonzero = find(squeeze(mrstft_loss(i,j,:)), 1,'last'); 
        data = squeeze(mrstft_loss(i, j, 1:last_nonzero));
        % compute the histogram 
        med_mrstft(i, j) = median(data); 
        std_mrstft(i, j) = std(data);
    end
end

med_edc = zeros(n_mics, n_mics);
std_edc = zeros(n_mics, n_mics);

for i = 1:length(div)
    for j = 1:length(div)
        % remove trailing zeros 
        last_nonzero = find(squeeze(edc_loss(i,j,:)), 1,'last'); 
        data = squeeze(edc_loss(i, j, 1:last_nonzero));
        % compute the histogram 
        med_edc(i, j) = median(data); 
        std_edc(i, j) = std(data);
    end
end

med_esr = zeros(n_mics, n_mics);
std_esr = zeros(n_mics, n_mics);

for i = 1:length(div)
    for j = 1:length(div)
        % remove trailing zeros 
        last_nonzero = find(squeeze(esr_loss(i,j,:)), 1,'last'); 
        data = squeeze(esr_loss(i, j, 1:last_nonzero));
        % compute the histogram 
        med_esr(i, j) = median(data); 
        std_esr(i, j) = std(data);
    end
end

% med_edc = triu(med_edc);
% med_power = triu(med_power);
% med_mrstft = triu(med_mrstft);
% med_esr = triu(med_esr);

%% make symmetric 
% % aftern normalization
% [n,m]=size(med_edc);
% 
% % med_edc = med_edc/max(med_edc,[],'all');
% med_edc = triu(med_edc,1)'+med_edc;
% med_edc = (med_edc - mean(med_edc, 'all'))/std(med_edc,0,'all');
% 
% % med_power = med_power/max(med_power,[],'all');
% med_power = triu(med_power,1)'+med_power;
% med_power = (med_power - mean(med_power, 'all'))/std(med_power,0,'all');
% 
% % med_mrstft = med_mrstft/max(med_mrstft,[],'all');
% med_mrstft = triu(med_mrstft,1)'+med_mrstft;
% med_mrstft = (med_mrstft - mean(med_mrstft, 'all'))/std(med_mrstft,0,'all');
% 
% med_esr = triu(med_esr,1)'+med_esr;
% med_esr = (med_esr - mean(med_esr, 'all'))/std(med_esr,0,'all');

%% plot the medians 
fig = figure(4);

c_min = -1.2316; 
c_max = 2.5129;

subplot(1, 4, 1); 
imagesc(med_esr); % axis image; axis ij; %colorbar; 
clim([c_min, c_max])
axis image;
colormap(mycolormap); % colorbar
hold on 
for i = 1:5
   plot([.5,5.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,5.5],'k-');
end
xlim([0.5, 5.5]); ylim([0.5, 5.5]);
xlabel('Microphone position', 'FontSize', 20); ylabel('Microphone position','FontSize',20)
set(gca,'Fontsize',16,'XTick', [1:5], 'XTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
set(gca,'Fontsize',16,'YTick', [1:5], 'YTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
title('$\mathcal{L}_{\textrm{ESR}}$')

subplot(1, 4, 2); 
imagesc(med_mrstft); % axis image; axis ij; %colorbar; 
clim([c_min, c_max])
axis image;
colormap(mycolormap); % colorbar
hold on 
for i = 1:5
   plot([.5,5.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,5.5],'k-');
end
xlim([0.5, 5.5]); ylim([0.5, 5.5]);
xlabel('Microphone position', 'FontSize', 20); ylabel('Microphone position','FontSize',20)
set(gca,'Fontsize',16,'XTick', [1:5], 'XTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
set(gca,'Fontsize',16,'YTick', [1:5], 'YTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
title('$\mathcal{L}_{\textrm{MSS}}$')

subplot(1, 4, 3); 
imagesc(med_power);  % axis image; axis ij; %colorbar;  
clim([c_min, c_max])
axis image;
colormap(mycolormap); % colorbar
hold on 
for i = 1:11
   plot([.5,11.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,11.5],'k-');
end
xlim([0.5, 5.5]); ylim([0.5, 5.5]);
xlabel('Microphone position', 'FontSize', 20); ylabel('Microphone position','FontSize',20)
set(gca,'Fontsize',16,'XTick', [1:5], 'XTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
set(gca,'Fontsize',16,'YTick', [1:5], 'YTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
title('$\mathcal{L}_{\textrm{PC}}$')

subplot(1, 4, 4);
imagesc(med_edc); % axis image;  %colorbar; 
clim([c_min, c_max])
axis image;
colormap(mycolormap); % colorbar
hold on 
for i = 1:11
   plot([.5,11.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,11.5],'k-');
end
xlim([0.5, 5.5]); ylim([0.5, 5.5]);
xlabel('Microphone position', 'FontSize', 20); ylabel('Microphone position','FontSize',20)
set(gca,'Fontsize',16,'XTick', [1:5], 'XTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
set(gca,'Fontsize',16,'YTick', [1:5], 'YTicklabel',{'1', '2', '3', '4', '5'},'fontname','Times')
title('$\mathcal{L}_{\textrm{EDC}}$')


h = axes(fig,'visible','off'); 
h.Title.Visible = 'on';
h.XLabel.Visible = 'on';
h.YLabel.Visible = 'on';
c = colorbar(h,'Position',[0.93 0.168 0.022 0.7]);  % attach colorbar to h
colormap(c,mycolormap)
clim(h,[c_min, c_max]);  
c.TickLabelInterpreter = 'latex';
c.FontSize = 16;
