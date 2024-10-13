clear all; close all; clc
% for plots 
set(groot, 'defaulttextinterpreter','latex');  
set(groot, 'defaultAxesTickLabelInterpreter','latex');  
set(groot, 'defaultLegendInterpreter','latex');

addpath("./Colormaps/")
mycolormap = customcolormap([0 .25 .5 .75 1], {'#9d0142','#f66e45','#ffffbb','#65c0ae','#5e4f9f'});

% load the data produced with the compute_losses python code 
mrstft = load("../data/dict_nclosed_mrstft.mat");
power = load("../data/dict_nclosed_power.mat");
edc = load("../data/dict_nclosed_edc.mat");
esr = load("../data/dict_nclosed_esr.mat");

mrstft_loss = cell2mat(mrstft.dict_mrstft);
power_loss = cell2mat(power.dict_power);
edc_loss = cell2mat(edc.dict_edc);
esr_loss = cell2mat(esr.dict_esr);
%% 
% normalize data // TODO normalize only non zero data 
means = [mean(mrstft_loss, 'all'), mean(power_loss, 'all'), mean(edc_loss, 'all'), mean(esr_loss, 'all')];
stds = [std(mrstft_loss,0, 'all'), std(power_loss,0, 'all'), std(edc_loss,0, 'all'), std(esr_loss,0, 'all')];
save('../data/means.mat',"means",'-mat')
save('../data/stds.mat',"stds",'-mat')
mrstft_loss = (mrstft_loss - mean(mrstft_loss, 'all'))/std(mrstft_loss,0,'all');
power_loss = (power_loss - mean(power_loss, 'all'))/std(power_loss,0,'all');
edc_loss = (edc_loss - mean(edc_loss, 'all'))/std(edc_loss,0,'all');
esr_loss = (esr_loss - mean(esr_loss, 'all'))/std(esr_loss,0,'all');

% generate sets of divisions
div = [];
for i = 0:5:50
    div = [div; [i, i+4]];
end
med_power = zeros(11, 11);
std_power = zeros(11, 11);

for i = 1:length(div)
    for j = 1:length(div)

        % remove trailing zeros 
        last_nonzero = find(squeeze(power_loss(i,j,:)), 1,'last'); 
        data = squeeze(power_loss(i, j, 1:last_nonzero));  
        med_power(i, j) = median(data); 
        std_power(i, j) = std(data);
    end
end
med_mrstft = zeros(11, 11);
std_mrstft = zeros(11, 11);

for i = 1:length(div)
    for j = 1:length(div)
        last_nonzero = find(squeeze(mrstft_loss(i,j,:)), 1,'last'); 
        data = squeeze(mrstft_loss(i, j, 1:last_nonzero));
        med_mrstft(i, j) = median(data); 
        std_mrstft(i, j) = std(data);
    end
end
med_edc = zeros(11, 11);
std_edc = zeros(11, 11);

for i = 1:length(div)
    for j = 1:length(div)
        last_nonzero = find(squeeze(edc_loss(i,j,:)), 1,'last'); 
        data = squeeze(edc_loss(i, j, 1:last_nonzero));
        med_edc(i, j) = median(data); 
        std_edc(i, j) = std(data);
    end
end
med_esr = zeros(11, 11);
std_esr = zeros(11, 11);

for i = 1:length(div)
    for j = 1:length(div)
        last_nonzero = find(squeeze(esr_loss(i,j,:)), 1,'last'); 
        data = squeeze(esr_loss(i, j, 1:last_nonzero));
        med_esr(i, j) = median(data); 
        std_esr(i, j) = std(data);
    end
end

%% plot the medians 

fig = figure(5);
load('pos.mat')
c_min = min([min(med_esr,[],'all'), min(med_mrstft,[],'all'), min(med_power,[],'all'), min(med_edc,[],'all')]);
c_max = max([max(med_esr,[],'all'), max(med_mrstft,[],'all'), max(med_power,[],'all'), max(med_edc,[],'all')]);

subplot(2, 5, [1, 2, 6, 7]);
imagesc(med_power); 
clim([c_min, c_max])
axis image;
colormap(mycolormap); 
hold on 
for i = 1:11
   plot([.5,11.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,11.5],'k-');
end
xlim([0.5, 11.5]); ylim([0.5, 11.5]);
xlabel('Number of reflective panels', 'FontSize', 30); ylabel('Number of reflective panels','FontSize',30)
set(gca,'Fontsize',20,'YTick', [1:11], 'YTicklabel',{'0--4', '5--9', '10--14', '15--19', '20--24', '25--29', '30--34', '35--39', '40--44', '45--49', '50--55'},'fontname','Times')
set(gca,'Fontsize',20,'XTick', [1:11], 'XTicklabel',{'0--4', '5--9', '10--14', '15--19', '20--24', '25--29', '30--34', '35--39', '40--44', '45--49', '50--55'},'fontname','Times')
title('$\mathcal{L}_{\textrm{PC}}$','Fontsize', 28)

subplot(2, 5, [3, 4, 8, 9]);
imagesc(med_edc); 
clim([c_min, c_max])
axis image;
colormap(mycolormap);
hold on 
for i = 1:11
   plot([.5,11.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,11.5],'k-');
end
xlim([0.5, 11.5]); ylim([0.5, 11.5]);
set(gca,'YTick',[])
set(gca,'Fontsize',20,'XTick', [1:11], 'XTicklabel',{'0--4', '5--9', '10--14', '15--19', '20--24', '25--29', '30--34', '35--39', '40--44', '45--49', '50--55'},'fontname','Times')
title('$\mathcal{L}_{\textrm{EDC}}$','Fontsize', 28)

subplot(2, 5, 5);
imagesc(med_mrstft);
clim([c_min, c_max])
axis image;
colormap(mycolormap);
hold on 
for i = 1:11
   plot([.5,11.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,11.5],'k-');
end
xlim([0.5, 11.5]); ylim([0.5, 11.5]);
set(gca,'XTick',[])
set(gca,'YTick',[])
title('$\mathcal{L}_{\textrm{ESR}}$','Fontsize', 20)

subplot(2, 5, 10);
imagesc(med_esr);
clim([c_min, c_max])
axis image;
colormap(mycolormap); 
hold on 
for i = 1:11
   plot([.5,11.5],[i-.5,i-.5],'k-');
   plot([i-.5,i-.5],[.5,11.5],'k-');
end
xlim([0.5, 11.5]); ylim([0.5, 11.5]);
set(gca,'XTick',[])
set(gca,'YTick',[])
title('$\mathcal{L}_{\textrm{MSS}}$', 'Fontsize', 20)


h = axes(fig,'visible','off'); 
h.Title.Visible = 'on';
h.XLabel.Visible = 'on';
h.YLabel.Visible = 'on';
c = colorbar(h,'Position',[0.93 0.168 0.022 0.7]);  % attach colorbar to h
colormap(c,mycolormap)
clim(h,[c_min, c_max]);  
c.TickLabelInterpreter = 'latex';
c.FontSize = 16;
