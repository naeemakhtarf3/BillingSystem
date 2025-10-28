# PowerShell script to test the active admissions endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admissions/active/list" -Method GET -ContentType "application/json"
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Response Status: $($_.Exception.Response.StatusCode)"
        Write-Host "Response Content: $($_.Exception.Response.Content)"
    }
}
