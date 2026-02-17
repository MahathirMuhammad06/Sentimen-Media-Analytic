<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\BackendApiService;

class HistoryController extends Controller
{
    protected $apiService;

    public function __construct(BackendApiService $apiService)
    {
        $this->apiService = $apiService;
    }

    /**
     * Display search history page
     */
    public function index()
    {
        $historyResponse = $this->apiService->getSearchHistory();
        $history = $historyResponse['success'] ? $historyResponse['data'] : [];

        return view('history', [
            'history' => $history
        ]);
    }

    /**
     * Show history detail with search results
     */
    public function detail(Request $request)
    {
        $query = $request->input('query');
        $timestamp = $request->input('timestamp');

        if (empty($query)) {
            return redirect()
                ->route('history')
                ->with('error', 'Invalid history item');
        }

        // Get articles for this search query
        $articlesResponse = $this->apiService->getArticles($query);
        $articles = $articlesResponse['success'] ? $articlesResponse['data'] : [];

        // Calculate sentiment stats
        $sentimentStats = $this->calculateSentimentStats($articles);
        
        // Calculate sources summary - INI YANG DITAMBAHKAN
        $sourcesSummary = $this->getSourcesSummary($articles);

        return view('history-detail', [
            'query'          => $query,
            'timestamp'      => $timestamp,
            'articles'       => $articles,
            'sentimentStats' => $sentimentStats,
            'sourcesSummary' => $sourcesSummary  // PASTIKAN INI ADA
        ]);
    }

    /**
     * Delete search history item (AJAX endpoint)
     */
    public function delete($historyId)
    {
        $response = $this->apiService->deleteSearchHistory($historyId);

        if ($response['success']) {
            return response()->json([
                'success' => true,
                'message' => 'Search history deleted'
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $response['message'] ?? 'Failed to delete history'
        ], 400);
    }

    /**
     * Clear all search history (AJAX endpoint)
     */
    public function clearAll()
    {
        $response = $this->apiService->clearAllSearchHistory();

        if ($response['success']) {
            return response()->json([
                'success' => true,
                'message' => 'All search history cleared'
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $response['message'] ?? 'Failed to clear history'
        ], 400);
    }

    /**
     * Calculate sentiment statistics from articles
     */
    private function calculateSentimentStats($articles)
    {
        $positif = 0;
        $negatif = 0;
        $netral  = 0;

        foreach ($articles as $article) {
            $raw = strtolower(trim($article['sentiment'] ?? 'neutral'));

            // NORMALISASI LABEL (EN → ID)
            switch ($raw) {
                case 'positive':
                case 'positif':
                    $positif++;
                    break;

                case 'negative':
                case 'negatif':
                    $negatif++;
                    break;

                case 'neutral':
                case 'netral':
                default:
                    $netral++;
                    break;
            }
        }

        $total = $positif + $negatif + $netral;
        $safeTotal = max(1, $total);

        return [
            'positif' => $positif,
            'negatif' => $negatif,
            'netral'  => $netral,
            'total'   => $total,
            'persen'  => [
                'positif' => round($positif / $safeTotal * 100, 1),
                'negatif' => round($negatif / $safeTotal * 100, 1),
                'netral'  => round($netral  / $safeTotal * 100, 1),
            ],
        ];
    }

    /**
     * Hitung jumlah berita per sumber
     * METHOD INI DITAMBAHKAN
     */
    private function getSourcesSummary($articles)
    {
        $sources = [];

        foreach ($articles as $article) {
            $source = $article['source'] ?? 'Unknown';
            
            if (!isset($sources[$source])) {
                $sources[$source] = 0;
            }
            
            $sources[$source]++;
        }

        // Convert to array format
        $result = [];
        foreach ($sources as $name => $count) {
            $result[] = [
                'name' => $name,
                'article_count' => $count
            ];
        }

        // Sort by count descending
        usort($result, function($a, $b) {
            return $b['article_count'] - $a['article_count'];
        });

        return $result;
    }
}