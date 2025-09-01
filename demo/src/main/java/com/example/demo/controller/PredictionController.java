package com.example.demo.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.http.MediaType;

import java.util.Map;

@Controller
public class PredictionController {

    private final WebClient webClient = WebClient.create("http://127.0.0.1:5000");


    @GetMapping("/")
    public String index(Model model) {
        // Fetch options from Flask API
        Map<String, Object> options = webClient.get()
                .uri("/options")
                .retrieve()
                .bodyToMono(Map.class)
                .block();

        model.addAttribute("DependentsList", options.get("DependentsList"));
        model.addAttribute("InternetServiceList", options.get("InternetServiceList"));
        model.addAttribute("OnlineSecurityList", options.get("OnlineSecurityList"));
        model.addAttribute("ContractList", options.get("ContractList"));
        model.addAttribute("StreamingTVList", options.get("StreamingTVList"));

        return "index";
    }

    @PostMapping("/predict")
    public String predict(
            @RequestParam String Dependents,
            @RequestParam String InternetService,
            @RequestParam String OnlineSecurity,
            @RequestParam String Contract,
            @RequestParam String StreamingTV,
            @RequestParam String MonthlyCharges,
            Model model) {

        Map<String, String> predictionResponse = webClient.post()
                .uri("/predict")
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .bodyValue(String.format(
                        "Dependents=%s&InternetService=%s&OnlineSecurity=%s&Contract=%s&StreamingTV=%s&MonthlyCharges=%s",
                        Dependents, InternetService, OnlineSecurity, Contract, StreamingTV, MonthlyCharges))
                .retrieve()
                .bodyToMono(Map.class)
                .block();

        model.addAttribute("prediction_value", predictionResponse.get("prediction"));
        return "prediction";
    }
}
