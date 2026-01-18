interface UploadedCsv {
  file: File;
  headers: string[];
  selectedHeaders: Set<string>;
}
