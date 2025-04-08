% https://en.wikipedia.org/wiki/Bloom_filter#Probability_of_false_positives

%%

%%%%%%%%%%%%%%%%%%%%%%
%%% THIS SECTION Shows the FP rate, sweeping over several NUM_HASH options.
%%% Here, it seems that #hash should PROBABLY be between 4 and 32.
%%% For smaller #hash, the FP rate is never close to zero.
%%% For larger #hash, the FP rate stays close to zero until some critical
%%% point when it shoots up very very quickly.

clf
num_hash_arr = [2, 4, 8, 12, 16, 32, 100];
n_over_m_arr = 0 : 1/5000 : 0.1 ;

plothandles = [];

for k = num_hash_arr
    hold on;
    FP_rate_exp_estimate = (1 - exp(-k.*n_over_m_arr)).^k;
    log_FP_rate = log(FP_rate_exp_estimate);

    legend_entry = sprintf("#hash = (%d)", k);

    plothandles(end+1) = plot(n_over_m_arr, log_FP_rate, "DisplayName", legend_entry);
    %plothandles(end+1) = plot(n_over_m_arr, FP_rate_exp_estimate, "DisplayName", legend_entry);

end

legend(plothandles);
title("FP Rate, #Hash vs (#Insertions / BV Length)")
xlabel("(#Insertions / BV Length)")
ylabel("Log(False Positive Rate)")

%%


%%%%%%%%%%%%%%%%%%%%%%
%%% THIS SECTION Shows how it behaves absolutely. You can plot the
%%% exponential estimate vs the ACTUAL behaviour and verify they are very very close.
%%% 
%%% You can also vary m and n separately, and show that the FP rate
%%% basically only depends on (n/m). (If you zoom in A LOT you see they
%%% don't overlap... but whatever).

%clf

num_hash_arr = [2, 5, 10, 20];
BV_Len_arr = 2.^(15:20);

for k = num_hash_arr
    
    f = figure;
    plothandles = [];
    hold on;
    
    for m = BV_Len_arr
        
        lgm = log2(m);
        n = [1:m]; % Number of insertions
        
        tmpval = (1 - 1./m);
        FP_rate_actual = (1 - tmpval.^(k*n)).^k;
        FP_rate_exp_estimate = (1 - exp(-k*n./m)).^k;
                
        legend_entry = sprintf("m = 2 \\^ (%d)", lgm);
        x_axis = linspace(0, 100, m);
        plothandles(end+1) = plot(x_axis, FP_rate_actual, ...
                                    "DisplayName", sprintf("m = 2 \\^ (%d) ACTUAL", lgm));
        plothandles(end+1) = plot(x_axis, FP_rate_exp_estimate, ...
                                    "DisplayName", sprintf("m = 2 \\^ (%d) ESTIMATE", lgm));
        
    end
    legend(plothandles);
    title(sprintf("Num_hash = %d", k));
end


