[ULGFileName, ULGPathName] = uigetfile('*.ulg','ULG File Query');
FolderPath = ULGPathName;
ulgpath = [ULGPathName ULGFileName];

% Takes a given path and ULG Filename and returns a cell array with
% relevant data taken from the ULG File

% Construct the file path, open the file, acquire the data delimited by
% white spaces, and close the file
ULGFile = fopen(ulgpath);
ULGRaw = textscan(ULGFile, '%s');
fclose(ULGFile);

% Open the raw data and remove the unnecessary rows
RawFilter = ULGRaw{1,1};
found = 0;
line = 1;
for i = 1:length(RawFilter)
    curLine = RawFilter{i};
    if length(curLine) >= 3 && isequal('0,1',curLine(1:3)) && found == 0
        found = 1;
        line = i;
    end
end
RawFilter = RawFilter(line:end,1);

% Initiate the final cell array.
ULGData = cell(length(RawFilter),7); % used to say 7 columns, -1 to length

% Loop through the entire raw data
for i = 1:length(RawFilter) % used to be -1
    % Create a delimited cell array of an individual cell component in the
    % raw data
    CellString = strsplit(RawFilter{i},',');
    % Loop through the delimited cell array
    for j = 1:length(CellString)
        % Assign the data from the delimited cell array within the final
        % cell array
        if j ~= 6 && j ~= 7
            ULGData{i,j} = str2num(CellString{j});
        elseif j == 6
            index_ps = strfind(CellString{j},'ps');
            newstring = CellString{j};
            newstring = newstring(1:index_ps+1);
            ULGData{i,j} = newstring;
            add = ['_' CellString{2} '_' CellString{2}];
            ULGData{i,j} = [newstring add];
        else
            ULGData{i,j} = CellString{j};
        end
    end
end

frames = length(ULGData(:,4));

dm3path = uigetdir(ULGPathName,'DM3 Path Query'); % script defaults to .dm3 files
dm3_files = dir([dm3path,'\*.dm3']);

ULGData = sortrows(ULGData,3);

first_dm3path = [dm3path '\' dm3_files(1).name];
first_dm3Data = DM3Import(first_dm3path);
first_img_data = first_dm3image_data';
cur_img_data = first_img_data;

DataTimeSort = flipud(sortrows(full_path_data,2));

New_place = strcat(dm3path, '/sorted');

mkdir(New_place);

w = waitbar(0, 'Copying and reordering files.');
count = 0;

for i = 1:length(DataTimeSort(:,2))
    count = count + 1;
    digits = numel(num2str(count));
    addzero = 4-digits; % change the number to change how many digits are shown in the resort. default 4 digits
    azString = '';
    for j = 1:addzero
        azString = [azString '0'];
    end
    curfile = [DataTimeSort{i,3} '\' DataTimeSort{i,4} '.dm3'];
    newfile = [New_place '\' azString num2str(count) '_' DataTimeSort{i,4} '.dm3'];
    copyfile(curfile, newfile);
    waitbar(count/frames);
end
close(w);