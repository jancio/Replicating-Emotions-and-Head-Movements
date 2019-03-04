%
% Author: Jan Ondras
% Institution: University of Cambridge
% Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
% Duration: October 2016 - May 2017
%
% Calculate ICC coefficients to evaluate inter-rater agreement in web survey




% Use ICC2.m with confidence intervals
% ICC(1, k) type
% Original publication: https://www.na-mic.org/Wiki/images/4/4b/Shrout_and_fleiss_ICC.pdf
% Matlab code used from: https://uk.mathworks.com/matlabcentral/fileexchange/22099-intraclass-correlation-coefficient--icc-

% 95% confidence interval
alpha = 0.05;

ICC_headPose = csvread('./surveyData/ICC_headPose.csv', 0, 1);
ICC_emotion0 = csvread('./surveyData/ICC_emotion0.csv', 0, 1);
ICC_emotion1 = csvread('./surveyData/ICC_emotion1.csv', 0, 1);
ICC_emotion2 = csvread('./surveyData/ICC_emotion2.csv', 0, 1);
ICC_emotion3 = csvread('./surveyData/ICC_emotion3.csv', 0, 1);
ICC_emotionsAll = csvread('./surveyData/ICC_emotionsAll.csv', 0, 1);
ICC_all = csvread('./surveyData/ICC_all.csv', 0, 1);

% Print: ICC, lowerBound, upperBound for every
[r, LB, UB, F, df1, df2, p] = ICC2(ICC_headPose, '1-k', alpha);
[r, LB, UB]
[r, LB, UB, F, df1, df2, p] = ICC2(ICC_emotion0, '1-k', alpha);
[r, LB, UB]
[r, LB, UB, F, df1, df2, p] = ICC2(ICC_emotion1, '1-k', alpha);
[r, LB, UB]
[r, LB, UB, F, df1, df2, p] = ICC2(ICC_emotion2, '1-k', alpha);
[r, LB, UB]
[r, LB, UB, F, df1, df2, p] = ICC2(ICC_emotion3, '1-k', alpha);
[r, LB, UB]
[r, LB, UB, F, df1, df2, p] = ICC2(ICC_emotionsAll, '1-k', alpha);
[r, LB, UB]
[r, LB, UB, F, df1, df2, p] = ICC2(ICC_all, '1-k', alpha);
[r, LB, UB]

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ICC_Calculate
% 
% ans =
%     0.7278    0.6328    0.8074
% 
% ans =
%     0.8896    0.8047    0.9489

% ans =
%     0.9212    0.8606    0.9635
% 
% ans =
%     0.8021    0.6498    0.9083
% 
% ans =
%     0.9398    0.8934    0.9721
% 
% ans =
%     0.9184    0.8899    0.9423
% 
% ans =
%     0.9055    0.8828    0.9256

% Just check against UNISTAT - Excel => CORRECT
x =[9	2	5	8
6	1	3	2
8	4	6	8
7	1	2	6
10	5	6	9
6	2	4	7];
[r, LB, UB, F, df1, df2, p] = ICC2(x, '1-k', alpha);
[r, LB, UB]

