<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\BackendApiService;

class MasterDataController extends Controller
{
    protected $apiService;

    public function __construct(BackendApiService $apiService)
    {
        $this->apiService = $apiService;
    }

    /**
     * Display master data page
     */
    public function index()
    {
        $sourcesResponse = $this->apiService->getSources();
        $sources = $sourcesResponse['success'] ? $sourcesResponse['data'] : [];

        return view('master-data', [
            'sources' => $sources
        ]);
    }

    /**
     * Get all sources (AJAX endpoint)
     */
    public function getSources()
    {
        $response = $this->apiService->getSources();

        if ($response['success']) {
            return response()->json([
                'success' => true,
                'data' => $response['data']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $response['message'] ?? 'Failed to fetch sources'
        ], 400);
    }

    /**
     * Create new source (AJAX endpoint)
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:100',
            'base_url' => 'required|url|max:500',
        ]);

        // Prepare data for backend
        $data = [
            'name' => $validated['name'],
            'base_url' => $validated['base_url'],
            'crawl_type' => 'auto',
            'config' => [
                'selectors' => [
                    'article_links' => 'a',
                    'title' => 'h1, .title',
                    'content' => 'article, .content, .article-body'
                ]
            ],
            'active' => true,
            'auto_detect' => true
        ];

        $response = $this->apiService->createSource($data);

        if ($response['success']) {
            return response()->json([
                'success' => true,
                'message' => 'Source added successfully',
                'data' => $response['data']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $response['message'] ?? 'Failed to add source'
        ], 400);
    }

    /**
     * Update source (AJAX endpoint)
     */
    public function update(Request $request, $sourceId)
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:100',
            'base_url' => 'sometimes|url|max:500',
            'active' => 'sometimes|boolean'
        ]);

        $response = $this->apiService->updateSource($sourceId, $validated);

        if ($response['success']) {
            return response()->json([
                'success' => true,
                'message' => 'Source updated successfully',
                'data' => $response['data']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $response['message'] ?? 'Failed to update source'
        ], 400);
    }

    /**
     * Delete source (AJAX endpoint)
     */
    public function destroy($sourceId)
    {
        $response = $this->apiService->deleteSource($sourceId);

        if ($response['success']) {
            return response()->json([
                'success' => true,
                'message' => 'Source deleted successfully'
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $response['message'] ?? 'Failed to delete source'
        ], 400);
    }
}