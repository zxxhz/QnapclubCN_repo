// 示例XML数据
const sampleXML = `<?xml version='1.0' encoding='utf-8'?>
<plugins>
  <cachechk>202511021353</cachechk>
  <item>
    <name>iPerf3</name>
    <changeLog></changeLog>
    <category>QnapclubCN Repo</category>
    <type>其他</type>
    <icon80>https://help.qnapclub.cn/upload/logo_80x80.png</icon80>
    <icon100>https://help.qnapclub.cn/upload/logo_100x100.png</icon100>
    <description>网络性能测试工具，用于测量网络带宽和质量</description>
    <fwVersion>4.2.6</fwVersion>
    <version>3.19.1</version>
    <platform>
      <platformID>TS-NASX86</platformID>
      <location>https://www.myqnap.org/repo/iPerf3_3.19.1_x86_64.qpkg</location>
      <signature></signature>
    </platform>
    <platform>
      <platformID>TS-NASARM_64</platformID>
      <location>https://www.myqnap.org/repo/iPerf3_3.19.1_arm_64.qpkg</location>
      <signature></signature>
    </platform>
    <internalName>iPerf3</internalName>
    <publishedDate>2025-10-19 14:21</publishedDate>
    <maintainer>QoolBox</maintainer>
    <developer>QoolBox</developer>
    <forumLink></forumLink>
    <language>English</language>
    <snapshot></snapshot>
    <bannerImg></bannerImg>
    <tutorialLink></tutorialLink>
  </item>
  <item>
    <name>Docker</name>
    <changeLog>更新Docker引擎到最新版本</changeLog>
    <category>QnapclubCN Repo</category>
    <type>虚拟化</type>
    <icon80>https://help.qnapclub.cn/upload/docker_80x80.png</icon80>
    <icon100>https://help.qnapclub.cn/upload/docker_100x100.png</icon100>
    <description>容器化平台，轻松部署和管理应用程序</description>
    <fwVersion>4.3.6</fwVersion>
    <version>24.0.7</version>
    <platform>
      <platformID>TS-NASX86</platformID>
      <location>https://www.myqnap.org/repo/Docker_24.0.7_x86_64.qpkg</location>
      <signature></signature>
    </platform>
    <platform>
      <platformID>TS-NASARM_64</platformID>
      <location>https://www.myqnap.org/repo/Docker_24.0.7_arm_64.qpkg</location>
      <signature></signature>
    </platform>
    <internalName>ContainerStation</internalName>
    <publishedDate>2025-11-01 09:15</publishedDate>
    <maintainer>QNAP</maintainer>
    <developer>Docker Inc</developer>
    <forumLink>https://forum.qnap.com</forumLink>
    <language>English</language>
    <snapshot></snapshot>
    <bannerImg></bannerImg>
    <tutorialLink>https://docs.qnap.com</tutorialLink>
  </item>
  <item>
    <name>FileStation</name>
    <changeLog>修复文件上传问题</changeLog>
    <category>QnapclubCN Repo</category>
    <type>文件管理</type>
    <icon80>https://help.qnapclub.cn/upload/filestation_80x80.png</icon80>
    <icon100>https://help.qnapclub.cn/upload/filestation_100x100.png</icon100>
    <description>强大的文件管理工具，支持远程访问和分享</description>
    <fwVersion>4.4.0</fwVersion>
    <version>5.2.1</version>
    <platform>
      <platformID>TS-NASX86</platformID>
      <location>https://www.myqnap.org/repo/FileStation_5.2.1_x86_64.qpkg</location>
      <signature></signature>
    </platform>
    <platform>
      <platformID>TS-NASARM_64</platformID>
      <location>https://www.myqnap.org/repo/FileStation_5.2.1_arm_64.qpkg</location>
      <signature></signature>
    </platform>
    <internalName>FileStation</internalName>
    <publishedDate>2025-10-28 16:30</publishedDate>
    <maintainer>QNAP</maintainer>
    <developer>QNAP</developer>
    <forumLink></forumLink>
    <language>简体中文</language>
    <snapshot></snapshot>
    <bannerImg></bannerImg>
    <tutorialLink></tutorialLink>
  </item>
</plugins>`;

// DOM元素
const xmlUrlInput = document.getElementById('xmlUrl');
const parseBtn = document.getElementById('parseBtn');
const sampleBtn = document.getElementById('sampleBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const appsGrid = document.getElementById('appsGrid');
const emptyState = document.getElementById('emptyState');
const stats = document.getElementById('stats');
const pagination = document.getElementById('pagination');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const currentPageEl = document.getElementById('currentPage');
const totalPagesEl = document.getElementById('totalPages');
const pageButtons = document.getElementById('pageButtons');
const searchSection = document.getElementById('searchSection');
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const searchInfo = document.getElementById('searchInfo');
const searchKeyword = document.getElementById('searchKeyword');
const searchCount = document.getElementById('searchCount');

// 分页和搜索变量
let allItems = [];
let filteredItems = [];
let currentPage = 1;
const itemsPerPage = 20;

// 解析XML并创建应用卡片
function parseAndDisplayApps(xmlString) {
    try {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlString, 'text/xml');
        
        // 检查解析错误
        if (xmlDoc.getElementsByTagName('parsererror').length > 0) {
            throw new Error('XML解析失败，请检查XML格式');
        }

        const items = xmlDoc.getElementsByTagName('item');
        const cachechk = xmlDoc.getElementsByTagName('cachechk')[0]?.textContent || '';
        
        if (items.length === 0) {
            showError('XML中没有找到应用数据');
            pagination.style.display = 'none';
            searchSection.style.display = 'none';
            searchInfo.style.display = 'none';
            return;
        }

        // 保存所有项目
        allItems = Array.from(items);
        filteredItems = [...allItems]; // 初始时显示所有项目
        currentPage = 1;

        // 显示统计信息
        displayStats(items, cachechk);
        
        // 显示搜索框
        searchSection.style.display = 'block';
        searchInfo.style.display = 'none';
        searchInput.value = '';
        clearSearchBtn.style.display = 'none';
        
        // 初始化分页
        renderPagination();

        // 显示结果
        emptyState.style.display = 'none';
        appsGrid.style.display = 'grid';
        hideError();

    } catch (error) {
        showError('解析失败：' + error.message);
        pagination.style.display = 'none';
        searchSection.style.display = 'none';
        searchInfo.style.display = 'none';
    }
}

// 执行搜索
function performSearch(keyword) {
    if (!keyword.trim()) {
        filteredItems = [...allItems];
        searchInfo.style.display = 'none';
        clearSearchBtn.style.display = 'none';
    } else {
        const lowerKeyword = keyword.toLowerCase();
        filteredItems = allItems.filter(item => {
            const name = getElementText(item, 'name').toLowerCase();
            const description = getElementText(item, 'description').toLowerCase();
            const developer = getElementText(item, 'developer').toLowerCase();
            const category = getElementText(item, 'category').toLowerCase();
            const type = getElementText(item, 'type').toLowerCase();
            
            return name.includes(lowerKeyword) ||
                   description.includes(lowerKeyword) ||
                   developer.includes(lowerKeyword) ||
                   category.includes(lowerKeyword) ||
                   type.includes(lowerKeyword);
        });
        
        // 显示搜索结果信息
        searchKeyword.textContent = keyword;
        searchCount.textContent = filteredItems.length;
        searchInfo.style.display = 'block';
        clearSearchBtn.style.display = 'block';
    }
    
    currentPage = 1;
    renderPagination();
}

// 渲染当前页
function renderCurrentPage() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentItems = filteredItems.slice(startIndex, endIndex);
    
    // 清空现有内容
    appsGrid.innerHTML = '';
    
    // 创建当前页的应用卡片
    currentItems.forEach((item, index) => {
        const card = createAppCard(item, startIndex + index);
        appsGrid.appendChild(card);
    });
}

// 渲染分页控件
function renderPagination() {
    const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    
    // 更新页码信息
    currentPageEl.textContent = currentPage;
    totalPagesEl.textContent = totalPages;
    
    // 更新上一页/下一页按钮状态
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages;
    
    // 生成页码按钮
    pageButtons.innerHTML = '';
    
    // 简化的页码显示逻辑
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // 调整起始页码，确保显示足够的页码
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // 添加页码按钮
    for (let i = startPage; i <= endPage; i++) {
        const btn = document.createElement('button');
        btn.className = `pagination-btn ${i === currentPage ? 'active' : ''}`;
        btn.textContent = i;
        btn.onclick = () => {
            currentPage = i;
            renderCurrentPage();
            renderPagination();
        };
        pageButtons.appendChild(btn);
    }
    
    // 显示分页控件
    pagination.style.display = 'flex';
    
    // 渲染当前页
    renderCurrentPage();
}

// 上一页
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderCurrentPage();
        renderPagination();
    }
});

// 下一页
nextPageBtn.addEventListener('click', () => {
    const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderCurrentPage();
        renderPagination();
    }
});

// 搜索输入事件
searchInput.addEventListener('input', () => {
    performSearch(searchInput.value);
});

// 搜索框回车事件
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
    }
});

// 清除搜索
clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    performSearch('');
});

// 创建应用卡片
function createAppCard(item, index) {
    const name = getElementText(item, 'name');
    const version = getElementText(item, 'version');
    const description = getElementText(item, 'description');
    const category = getElementText(item, 'category');
    const type = getElementText(item, 'type');
    const maintainer = getElementText(item, 'maintainer');
    const developer = getElementText(item, 'developer');
    const publishedDate = getElementText(item, 'publishedDate');
    const fwVersion = getElementText(item, 'fwVersion');
    
    // 获取图标，优先使用100x100，如果没有则使用80x80
    const icon100 = getElementText(item, 'icon100');
    const icon80 = getElementText(item, 'icon80');
    const icon = icon100 || icon80 || `https://picsum.photos/seed/${name}/100/100.jpg`;
    
    // 获取平台信息
    const platforms = [];
    const platformElements = item.getElementsByTagName('platform');
    Array.from(platformElements).forEach(platform => {
        const platformID = getElementText(platform, 'platformID');
        const location = getElementText(platform, 'location');
        if (platformID && location) {
            platforms.push({ id: platformID, url: location });
        }
    });

    const card = document.createElement('div');
    card.className = 'app-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    card.innerHTML = `
        <div class="app-header">
            <img src="${icon}" alt="${name}" class="app-icon" onerror="this.src='https://picsum.photos/seed/default/60/60.jpg'">
            <div class="app-info">
                <div class="app-name">${name}</div>
                <div class="app-version">
                    <span class="version-badge">v${version}</span>
                    <span>固件: ${fwVersion}</span>
                </div>
            </div>
        </div>
        <div class="app-body">
            <div class="app-description">${description || '暂无描述'}</div>
            <div class="app-meta">
                <div class="meta-item">
                    <span class="meta-label">分类</span>
                    <span class="meta-value">${category}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">类型</span>
                    <span class="meta-value">${type}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">开发者</span>
                    <span class="meta-value">${developer}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">发布时间</span>
                    <span class="meta-value">${formatDate(publishedDate)}</span>
                </div>
            </div>
            ${platforms.length > 0 ? `
            <div class="platforms">
                <div class="platforms-title">支持平台</div>
                <div class="platform-tags">
                    ${platforms.map(p => `<span class="platform-tag">${p.id}</span>`).join('')}
                </div>
            </div>
            ` : ''}
            ${platforms.length > 0 ? `
            <button class="download-btn" onclick="downloadApp('${name}', ${JSON.stringify(platforms).replace(/"/g, '&quot;')})")">
                下载应用
            </button>
            ` : ''}
        </div>
    `;
    
    return card;
}

// 获取元素文本内容
function getElementText(parent, tagName) {
    const element = parent.getElementsByTagName(tagName)[0];
    return element ? element.textContent.trim() : '';
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    } catch {
        return dateString;
    }
}

// 显示统计信息
function displayStats(items, cachechk) {
    const categories = new Set();
    Array.from(items).forEach(item => {
        const category = getElementText(item, 'category');
        if (category) categories.add(category);
    });

    document.getElementById('totalCount').textContent = items.length;
    document.getElementById('categories').textContent = categories.size;
    
    if (cachechk) {
        const formattedDate = cachechk.replace(/(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1-$2-$3 $4:$5');
        document.getElementById('lastUpdate').textContent = formattedDate;
    }
    
    stats.style.display = 'block';
}

// 下载应用
function downloadApp(name, platforms) {
    if (platforms.length === 1) {
        window.open(platforms[0].url, '_blank');
    } else {
        // 如果有多个平台，创建选择对话框
        const platformList = platforms.map((p, i) => `${i + 1}. ${p.id}`).join('\n');
        const choice = prompt(`请选择下载平台：\n${platformList}\n\n请输入序号 (1-${platforms.length})`);
        
        if (choice && !isNaN(choice)) {
            const index = parseInt(choice) - 1;
            if (index >= 0 && index < platforms.length) {
                window.open(platforms[index].url, '_blank');
            }
        }
    }
}

// 显示错误信息
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    loading.style.display = 'none';
    appsGrid.style.display = 'none';
    stats.style.display = 'none';
}

// 隐藏错误信息
function hideError() {
    errorMessage.style.display = 'none';
}

// 从URL获取XML - 直接从本机访问
async function fetchXML(url) {
    try {
        // 直接从本机访问URL，不使用代理
        const response = await fetch(url, {
            method: 'GET',
            mode: 'cors', // 使用CORS模式
            headers: {
                'Accept': 'application/xml, text/xml'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        
        const xmlText = await response.text();
        return xmlText;
    } catch (error) {
        // 处理跨域错误和其他错误
        if (error.message.includes('CORS')) {
            throw new Error('跨域访问被阻止。请确保XML文件配置了正确的CORS头，或使用本地服务器访问。');
        } else if (error.message.includes('Failed to fetch')) {
            throw new Error('无法连接到服务器，请检查网络连接或URL是否正确。');
        } else {
            throw new Error('获取XML文件失败: ' + error.message);
        }
    }
}

// 解析按钮点击事件
parseBtn.addEventListener('click', async () => {
    const url = xmlUrlInput.value.trim();
    
    if (!url) {
        showError('请输入XML文件网址');
        return;
    }

    // 验证URL格式
    try {
        new URL(url);
    } catch {
        showError('请输入有效的网址');
        return;
    }

    loading.style.display = 'block';
    hideError();
    parseBtn.disabled = true;

    try {
        const xmlText = await fetchXML(url);
        parseAndDisplayApps(xmlText);
    } catch (error) {
        showError(error.message);
    } finally {
        loading.style.display = 'none';
        parseBtn.disabled = false;
    }
});

// 示例按钮点击事件
sampleBtn.addEventListener('click', () => {
    xmlUrlInput.value = 'https://example.com/plugins.xml';
    parseAndDisplayApps(sampleXML);
});

// 回车键触发解析
xmlUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        parseBtn.click();
    }
});

// 页面加载时隐藏网格
appsGrid.style.display = 'none';

// 修复下载按钮的引号转义问题
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('download-btn')) {
        e.preventDefault();
        const appName = e.target.getAttribute('data-app-name');
        const platformsStr = e.target.getAttribute('data-platforms');
        try {
            const platforms = JSON.parse(platformsStr);
            downloadApp(appName, platforms);
        } catch (err) {
            console.error('解析平台数据失败:', err);
        }
    }
});

// 修改createAppCard函数中的下载按钮处理
function createAppCardFixed(item, index) {
    const name = getElementText(item, 'name');
    const version = getElementText(item, 'version');
    const description = getElementText(item, 'description');
    const category = getElementText(item, 'category');
    const type = getElementText(item, 'type');
    const maintainer = getElementText(item, 'maintainer');
    const developer = getElementText(item, 'developer');
    const publishedDate = getElementText(item, 'publishedDate');
    const fwVersion = getElementText(item, 'fwVersion');
    
    // 获取图标，优先使用100x100，如果没有则使用80x80
    const icon100 = getElementText(item, 'icon100');
    const icon80 = getElementText(item, 'icon80');
    const icon = icon100 || icon80 || `https://picsum.photos/seed/${name}/100/100.jpg`;
    
    // 获取平台信息
    const platforms = [];
    const platformElements = item.getElementsByTagName('platform');
    Array.from(platformElements).forEach(platform => {
        const platformID = getElementText(platform, 'platformID');
        const location = getElementText(platform, 'location');
        if (platformID && location) {
            platforms.push({ id: platformID, url: location });
        }
    });

    const card = document.createElement('div');
    card.className = 'app-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    card.innerHTML = `
        <div class="app-header">
            <img src="${icon}" alt="${name}" class="app-icon" onerror="this.src='https://picsum.photos/seed/default/60/60.jpg'">
            <div class="app-info">
                <div class="app-name">${name}</div>
                <div class="app-version">
                    <span class="version-badge">v${version}</span>
                    <span>固件: ${fwVersion}</span>
                </div>
            </div>
        </div>
        <div class="app-body">
            <div class="app-description">${description || '暂无描述'}</div>
            <div class="app-meta">
                <div class="meta-item">
                    <span class="meta-label">分类</span>
                    <span class="meta-value">${category}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">类型</span>
                    <span class="meta-value">${type}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">开发者</span>
                    <span class="meta-value">${developer}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">发布时间</span>
                    <span class="meta-value">${formatDate(publishedDate)}</span>
                </div>
            </div>
            ${platforms.length > 0 ? `
            <div class="platforms">
                <div class="platforms-title">支持平台</div>
                <div class="platform-tags">
                    ${platforms.map(p => `<span class="platform-tag">${p.id}</span>`).join('')}
                </div>
            </div>
            ` : ''}
            ${platforms.length > 0 ? `
            <button class="download-btn" data-app-name="${name}" data-platforms='${JSON.stringify(platforms)}'>
                下载应用
            </button>
            ` : ''}
        </div>
    `;
    
    return card;
}

// 替换原来的createAppCard函数
window.createAppCard = createAppCardFixed;