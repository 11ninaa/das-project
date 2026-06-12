package com.example.demo.services;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Utility class for executing Python scripts and parsing JSON responses.
 */
@Component
public class PythonScriptExecutor {
    
    private static final String PYTHON_EXECUTABLE = "python";
    private static final String PROJECT_ROOT_NAME = "Domasna4";
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    private File findProjectRoot() {
        String currentDir = System.getProperty("user.dir");
        File currentFile = new File(currentDir);
        File projectRoot = currentFile;
        
        while (projectRoot != null && !projectRoot.getName().equals(PROJECT_ROOT_NAME)) {
            File parent = projectRoot.getParentFile();
            if (parent == null) {
                break;
            }
            projectRoot = parent;
        }
        
        if (projectRoot == null || !projectRoot.getName().equals(PROJECT_ROOT_NAME)) {
            projectRoot = currentFile.getParentFile();
        }
        
        return projectRoot;
    }
    public Map<String, Object> executeScript(String scriptPath, int timeoutSeconds, String... args) {
        File projectRoot = findProjectRoot();
        if (projectRoot == null) {
            throw new RuntimeException(
                String.format("Could not find project root (%s). Current directory: %s", 
                    PROJECT_ROOT_NAME, System.getProperty("user.dir"))
            );
        }
        
        File scriptFile = new File(projectRoot, scriptPath);
        String scriptAbsolutePath = scriptFile.getAbsolutePath();
        
        if (!scriptFile.exists()) {
            throw new RuntimeException(
                String.format("Python script not found at: %s\n" +
                    "Project root: %s\n" +
                    "Please verify the script exists at: %s/%s",
                    scriptAbsolutePath, 
                    projectRoot.getAbsolutePath(),
                    PROJECT_ROOT_NAME, scriptPath)
            );
        }
        
        String[] command = new String[args.length + 2];
        command[0] = PYTHON_EXECUTABLE;
        command[1] = scriptAbsolutePath;
        System.arraycopy(args, 0, command, 2, args.length);
        
        ProcessBuilder processBuilder = new ProcessBuilder(command);
        File scriptDir = scriptFile.getParentFile();
        processBuilder.directory(scriptDir);
        processBuilder.redirectErrorStream(true);
        
        try {
            Process process = processBuilder.start();
            
            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }
            }
            
            boolean finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS);
            
            if (!finished) {
                process.destroyForcibly();
                throw new RuntimeException(
                    String.format("Python script timed out after %d seconds: %s", 
                        timeoutSeconds, scriptPath)
                );
            }
            
            if (process.exitValue() != 0) {
                String errorOutput = output.toString();
                String errorMessage = extractErrorMessage(errorOutput);
                throw new RuntimeException(
                    String.format("Python script failed (exit code %d): %s", 
                        process.exitValue(), errorMessage)
                );
            }
            
            String jsonOutput = extractJsonFromOutput(output.toString());
            
            if (jsonOutput.isEmpty()) {
                throw new RuntimeException("Python script returned empty output");
            }
            
            try {
                return objectMapper.readValue(jsonOutput, Map.class);
            } catch (Exception e) {
                throw new RuntimeException(
                    String.format("Failed to parse JSON output: %s\nError: %s", 
                        jsonOutput, e.getMessage())
                );
            }
            
        } catch (RuntimeException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException(
                String.format("Failed to execute Python script: %s\nError: %s", 
                    scriptPath, e.getMessage()), e
            );
        }
    }
    
    private String extractErrorMessage(String output) {
        String[] lines = output.split("\n");
        for (String line : lines) {
            line = line.trim();
            if (line.startsWith("{")) {
                try {
                    Map<String, Object> errorJson = objectMapper.readValue(line, Map.class);
                    if (errorJson.containsKey("error")) {
                        return (String) errorJson.get("error");
                    }
                } catch (Exception e) {
                }
            }
        }
        return output.length() > 500 ? output.substring(0, 500) + "..." : output;
    }
    
    private String extractJsonFromOutput(String output) {
        String trimmed = output.trim();
        
        if (!trimmed.contains("\n")) {
            return trimmed;
        }
        
        String[] lines = trimmed.split("\n");
        for (String line : lines) {
            line = line.trim();
            if (line.startsWith("{")) {
                return line;
            }
        }
        
        return trimmed;
    }
}



