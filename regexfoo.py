filename = input("What's the file name of the document to edit? > ")
file = open(filename, "r")
content = file.read()
file.close()
content.replace("{{media url=\"", "https://www.coreelectronics.com.au/media/")
content.replace("}}", "")
outputFilename = "corrected_"+filename
outputFile = open(outputFilename, "w")
outputFile.write(content)
print(content)
input("Press enter to close...")
outputFile.close()