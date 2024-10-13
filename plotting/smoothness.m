close all; clear all; clc

set(groot, 'defaulttextinterpreter','latex');  
set(groot, 'defaultAxesTickLabelInterpreter','latex');  
set(groot, 'defaultLegendInterpreter','latex');

% load("/Users/dalsag1/Dropbox (Aalto)/aalto/projects/asilomar24-rir-similarity/git/data/smooth_losses_mic2.mat")
load("/Users/dalsag1/Dropbox (Aalto)/aalto/projects/rir-similarity-metrics/asilomar24-rir-similarity/git/data/smooth_losses_mic2.mat")
colors = {[239,95,40], [0,135,255], [0,199,87], [236,179,48], [228,57,215], [168,168,168], [105,105,105]};
power_loss = normalize2(power_loss,  num_closed);
mrstft_loss = normalize2(mrstft_loss, num_closed);
edc_loss = normalize2(edc_loss, num_closed);
esr_loss = normalize2(esr_loss, num_closed);

n_closed = 1:55;
figure; hold on; 
xline(20, '--','Color','k','LineWidth',1,'HandleVisibility','off');
box on
meds_esr = [];
meds_mrstft = [];
meds_power = [];
meds_edc = [];
for i = 1:55
    indx = num_closed == i;
    pp{1} = plot_dist(i, esr_loss(indx),colors{7}/255);
    meds_esr = [meds_esr, median(esr_loss(indx))];
    pp{2} = plot_dist(i, mrstft_loss(indx),colors{3}/255');
    meds_mrstft = [meds_mrstft,  median(mrstft_loss(indx))];
    pp{3} = plot_dist(i, power_loss(indx),colors{1}/255);
    meds_power = [meds_power,  median(power_loss(indx))];
    pp{4} = plot_dist(i, edc_loss(indx),colors{2}/255);
    meds_edc = [meds_edc,  median(edc_loss(indx))];
end
plot([1:55], meds_esr, '-', 'MarkerSize',6,'Color', colors{7}/255);
plot([1:55], meds_mrstft, '-', 'MarkerSize',6,'Color', colors{3}/255);
plot([1:55], meds_power, '-', 'MarkerSize',6,'Color', colors{1}/255);
plot([1:55], meds_edc, '-', 'MarkerSize',6,'Color', colors{2}/255);
grid minor
h = legend([pp{:}], {'$\mathcal{L}_{\textrm{ESR}}$','$\mathcal{L}_{\textrm{MSS}}$','$\mathcal{L}_{\textrm{PC}}$', '$\mathcal{L}_{\textrm{EDC}}$'}, 'FontSize', 16, 'Orientation', 'horizontal', 'Location', 'northoutside')
%set(h,'Orientation', 'horizontal', 'Location', 'northoutside')

set(gca,'Fontsize',16,'XTick', [0:5:55], 'XTicklabel',[0:5:55]-20,'fontname','Times')
set(gca,'YTick',[])
%xlim([0, 55]);
%ylim([0 1])
xlabel('$\Delta$ number of reflective panels', 'FontSize',20);
ylabel('Loss value', 'FontSize',20)

set(gca,'Fontsize',20)
ylim([-0.10 0.9])
xlim([0, 55])
%% Functions 
function p =  plot_dist(n, vals, color)
    med = median(vals);
    stand = std(vals,0,"all");
    y1 = med - stand/2;
    y2 = med + stand/2;
    line([n n], [y1 y2], 'Color', [color, 0.4], 'LineWidth', 2, 'MarkerSize', 14); hold on
    p = plot(n, med, '.', 'MarkerSize',14,'Color', color);
end

function y = normalize(x)
    y = (x - mean(x,"all"))/std(x,0,"all");
end
function y = normalize2(x, num_closed)
    y = (x-min(x))/(max(x)-min(x));
    y = y - median(y(num_closed==20));
end