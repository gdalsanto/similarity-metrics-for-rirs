clear all; close all; clc

set(groot, 'defaulttextinterpreter','latex');  
set(groot, 'defaultAxesTickLabelInterpreter','latex');  
set(groot, 'defaultLegendInterpreter','latex');


mixingtime = load("../data/mixing_time.mat");

medians = [];
stds = [];
for i = 0:55
    medians = [medians, median(mixingtime.t_abel(mixingtime.num_closed == i))];
    stds = [stds, std(mixingtime.t_abel(mixingtime.num_closed == i), 0, 'all')];
end
plot(mixingtime.num_closed, mixingtime.t_abel, '.', 'Color', [190,190,190]./255), hold on; 
grid minor

for i = 1:56
    y1 = medians(i) - stds(i)/2;
    y2 = medians(i) + stds(i)/2;
    line([i-1 i-1], [y1 y2], 'Color', 'k', 'Marker', "_", 'LineWidth', 1, 'MarkerSize', 8); hold on
end
plot(0:55,medians, '.', 'Color','k', 'MarkerSize', 12)
xlim([-0.5, 55.5])
ylim([5, 40])
xlabel('Number of reflective panels', 'FontSize',24)
ylabel('Mixing time (ms)', 'FontSize',24)
set(gca,'Fontsize',20)
