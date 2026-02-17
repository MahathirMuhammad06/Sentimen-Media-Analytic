<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\BackendApiService;

class DashboardController extends Controller
{
    protected $apiService;

    public function __construct(BackendApiService $apiService)
    {
        $this->apiService = $apiService;
    }

    /**
     * DASHBOARD
     */
    public function index()
    {
        // Ambil semua artikel
        $articlesResponse = $this->apiService->getArticles();
        $allArticles = $articlesResponse['success'] ? $articlesResponse['data'] : [];

        // Hitung sentimen
        $sentiment = $this->calculateSentimentStats($allArticles);

        // Format stats
        $stats = [
            'positive_count' => $sentiment['positif'],
            'negative_count' => $sentiment['negatif'],
            'neutral_count'  => $sentiment['netral'],
            'total_articles' => $sentiment['total'],
        ];

        // Ambil berita terbaru
        $recentResponse = $this->apiService->getRecentArticles(10);
        $recentArticles = $recentResponse['success'] ? $recentResponse['data'] : [];

        // Ambil summary sumber untuk tabel
        $sourcesSummary = $this->getSourcesSummary($allArticles);

        return view('dashboard', compact('stats', 'recentArticles', 'sourcesSummary'));
    }

    /**
     * SEARCH
     */
    public function search(Request $request)
    {
        $query = trim($request->input('query'));

        if ($query === '') {
            return redirect()->route('dashboard')
                ->with('error', 'Kata kunci pencarian tidak boleh kosong');
        }

        $this->apiService->saveSearchHistory($query);

        $articlesResponse = $this->apiService->getArticles($query);
        $articles = $articlesResponse['success'] ? $articlesResponse['data'] : [];

        $sentimentStats = $this->calculateSentimentStats($articles);
        $sourcesSummary = $this->getSourcesSummary($articles);

        return view('search-results', [
            'query'          => $query,
            'articles'       => $articles,
            'sentimentStats' => $sentimentStats,
            'sourcesSummary' => $sourcesSummary,
        ]);
    }

    /**
     * Hitung sentimen
     */
    private function calculateSentimentStats($articles)
    {
        $positif = 0;
        $negatif = 0;
        $netral  = 0;

        foreach ($articles as $article) {
            $sentiment = strtolower($article['sentiment'] ?? 'neutral');

            if (in_array($sentiment, ['positive', 'positif'])) {
                $positif++;
            } elseif (in_array($sentiment, ['negative', 'negatif'])) {
                $negatif++;
            } else {
                $netral++;
            }
        }

        return [
            'positif' => $positif,
            'negatif' => $negatif,
            'netral'  => $netral,
            'total'   => $positif + $negatif + $netral,
        ];
    }

    /**
     * Hitung jumlah berita per sumber
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