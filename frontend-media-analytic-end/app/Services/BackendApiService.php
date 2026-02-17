<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Http\Client\Response;

class BackendApiService
{
    private $baseUrl;
    private $timeout;

    public function __construct()
    {
        $this->baseUrl = env('BACKEND_API_URL', 'http://localhost:5000');
        $this->timeout = 30; // 30 seconds timeout
    }

    /**
     * Get all articles with optional filters
     */
    public function getArticles($query = null, $source = null)
    {
        try {
            $params = [];
            if ($query) $params['q'] = $query;
            if ($source) $params['source'] = $source;

            $response = Http::timeout($this->timeout)
                ->get("{$this->baseUrl}/v1/articles", $params);

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to fetch articles',
                'data' => []
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::getArticles - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => []
            ];
        }
    }

    /**
     * Get article detail by ID
     */
    public function getArticle($articleId)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->get("{$this->baseUrl}/v1/article/{$articleId}");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Article not found',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::getArticle - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Get dashboard statistics
     */
    public function getDashboardStats()
    {
        try {
            $response = Http::timeout($this->timeout)
                ->get("{$this->baseUrl}/v1/dashboard/stats");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to fetch dashboard stats',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::getDashboardStats - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Get recent articles for dashboard
     */
    public function getRecentArticles($limit = 10)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->get("{$this->baseUrl}/v1/dashboard/articles/recent", [
                    'limit' => $limit
                ]);

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to fetch recent articles',
                'data' => []
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::getRecentArticles - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => []
            ];
        }
    }

    /**
     * Add article to favorites
     */
    public function addFavorite($articleId)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->post("{$this->baseUrl}/v1/favorites/{$articleId}");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => $response->json()['detail'] ?? 'Failed to add favorite',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::addFavorite - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Remove article from favorites
     */
    public function removeFavorite($articleId)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->delete("{$this->baseUrl}/v1/favorites/{$articleId}");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to remove favorite',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::removeFavorite - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Get all favorite articles
     */
public function getFavorites($limit = 100)
{
    try {
        $response = Http::timeout($this->timeout)
            ->get("{$this->baseUrl}/v1/favorites", [
                'limit' => $limit
            ]);

        if ($response->successful()) {
            return [
                'success' => true,
                'data' => $response->json() ?? [] // 🔥 PASTI ARRAY
            ];
        }

        return [
            'success' => false,
            'message' => 'Failed to fetch favorites',
            'data' => []
        ];
    } catch (\Exception $e) {
        Log::error('BackendApiService::getFavorites - ' . $e->getMessage());
        return [
            'success' => false,
            'message' => $e->getMessage(),
            'data' => []
        ];
    }
}


    /**
     * Check if article is favorite
     */
    public function checkFavorite($articleId)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->get("{$this->baseUrl}/v1/favorites/{$articleId}/check");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to check favorite',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::checkFavorite - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Save search to history
     */
    public function saveSearchHistory($keyword)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->asForm()
                ->post("{$this->baseUrl}/v1/search-history?keyword=" . urlencode($keyword));

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to save search history',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::saveSearchHistory - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Get search history
     */
    public function getSearchHistory($limit = 50)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->get("{$this->baseUrl}/v1/search-history", [
                    'limit' => $limit
                ]);

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to fetch search history',
                'data' => []
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::getSearchHistory - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => []
            ];
        }
    }

    /**
     * Delete search history item
     */
    public function deleteSearchHistory($historyId)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->delete("{$this->baseUrl}/v1/search-history/{$historyId}");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to delete search history',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::deleteSearchHistory - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Clear all search history
     */
    public function clearAllSearchHistory()
    {
        try {
            $response = Http::timeout($this->timeout)
                ->delete("{$this->baseUrl}/v1/search-history");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to clear search history',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::clearAllSearchHistory - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Get all news sources
     */
    public function getSources()
    {
        try {
            $response = Http::timeout($this->timeout)
                ->get("{$this->baseUrl}/v1/sources");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to fetch sources',
                'data' => []
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::getSources - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => []
            ];
        }
    }

    /**
     * Create new news source
     */
    public function createSource($data)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->post("{$this->baseUrl}/v1/sources", $data);

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => $response->json()['detail'] ?? 'Failed to create source',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::createSource - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Update news source
     */
    public function updateSource($sourceId, $data)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->put("{$this->baseUrl}/v1/sources/{$sourceId}", $data);

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to update source',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::updateSource - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Delete news source
     */
    public function deleteSource($sourceId)
    {
        try {
            $response = Http::timeout($this->timeout)
                ->delete("{$this->baseUrl}/v1/sources/{$sourceId}");

            if ($response->successful()) {
                return [
                    'success' => true,
                    'data' => $response->json()
                ];
            }

            return [
                'success' => false,
                'message' => 'Failed to delete source',
                'data' => null
            ];
        } catch (\Exception $e) {
            Log::error('BackendApiService::deleteSource - ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'data' => null
            ];
        }
    }

    /**
     * Check backend health
     */
    public function checkHealth()
    {
        try {
            $response = Http::timeout(5)
                ->get("{$this->baseUrl}/health");

            return $response->successful();
        } catch (\Exception $e) {
            Log::error('BackendApiService::checkHealth - ' . $e->getMessage());
            return false;
        }
    }
}