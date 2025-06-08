package main

import (
	"context"
	"crypto/tls"
	"fmt"
	"log"
	"time"

	"github.com/gospider007/requests"
)

func main() {
	ctx := context.Background()
	client, err := requests.NewClient(context.Background())

	if err != nil {
		log.Fatal("Failed to create client:", err)
	}

	// Customize the request
	clientOptions := requests.ClientOption{
		H3:                    true,
		Ja3:                   true,
		ForceHttp1:            false,
		DisCookie:             false,
		DisDecode:             false,
		DisUnZip:              false,
		DisAlive:              false,
		Timeout:               30 * time.Second,
		ResponseHeaderTimeout: 15 * time.Second,
		TlsHandshakeTimeout:   10 * time.Second,
		KeepAlive:             10 * time.Second,
		TlsConfig:             &tls.Config{InsecureSkipVerify: true},
		Headers: map[string]string{
			"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHgwNzU1ODgxNWFmMjc5MGIzYmIxNGY3ODIwNDZiODdkOTk1YjQzYmUwIiwiaXNzIjoiaHR0cHM6Ly9hcGkudW5pd2hhbGVzLmlvLyIsInN1YiI6InVzZXIiLCJwbGFuIjoiYmFzaWMiLCJiYWxhbmNlIjowLCJpYXQiOjE3MzA3ODk1MjEsImV4cCI6MTczMDgwMDMyMX0.YIa_kRAiX0QDkcz5hXTKv0_C2eERJJt6KpookCFwMTo",
		},
	}

	client, err = requests.NewClient(ctx, clientOptions)
	if err != nil {
		log.Fatal("Failed to create client:", err)
	}
	response, err := client.Get(ctx, "https://feed-api.cielo.finance/v1/leaderboard/tag")
	if err != nil {
		log.Fatal("Request failed:", err)
	}
	defer response.CloseBody()

	// Print response status and headers
	fmt.Println("Response Status:", response.Status())
	fmt.Println("Response Headers:", response.Headers())
	// fmt.Println("Response Cookies:", response.Cookies())
	// fmt.Println(("Response Content:"), response.Text())

}
