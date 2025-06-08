package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

// func main() {
	start := time.Now() // Record the start time

	numThreads := 25
	var wg sync.WaitGroup
	pageCh := make(chan int, 100)

	for i := 1; i <= 100; i++ {
		pageCh <- i
	}
	close(pageCh)

	for i := 0; i < numThreads; i++ {
		wg.Add(1)
		go func(threadID int) {
			defer wg.Done()
			for page := range pageCh {
				printStatusCode(threadID, page)
			}
		}(i)
	}

	wg.Wait()

	elapsed := time.Since(start) // Calculate the elapsed time
	fmt.Printf("All requests completed in %s\n", elapsed)
}

func printStatusCode(threadID, page int) {
	client := &http.Client{}
	url := fmt.Sprintf("https://feed-api.cielo.finance/v1/leaderboard/tag?type=solana&page=%d", page)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Set("authorization", "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHgwNzU1ODgxNWFmMjc5MGIzYmIxNGY3ODIwNDZiODdkOTk1YjQzYmUwIiwiaXNzIjoiaHR0cHM6Ly9hcGkudW5pd2hhbGVzLmlvLyIsInN1YiI6InVzZXIiLCJwbGFuIjoiYmFzaWMiLCJiYWxhbmNlIjowLCJpYXQiOjE3MzAwNTc5MTIsImV4cCI6MTczMDA2ODcxMn0.f0GbCb6gdm7RZkS4pX1xTJT-QtMMe1N7eI4YMkjmi1A")
	req.Header.Set("user-agent", "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36")

	for {
		resp, err := client.Do(req)
		if err != nil {
			log.Fatal(err)
		}
		defer resp.Body.Close()

		if resp.StatusCode == http.StatusTooManyRequests {
			coolOff := time.Duration(5+rand.Intn(6)) * time.Second
			fmt.Printf("Thread %d: Page %d: Rate limited. Retrying after %v\n", threadID, page, coolOff)
			time.Sleep(coolOff)
		} else {
			fmt.Printf("Thread %d: Page %d: %d\n", threadID, page, resp.StatusCode)
			break
		}
	}
}
