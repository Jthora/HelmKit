//
//  NotchSprite.swift
//  HelmKit
//
//  Created by Jordan Trana on 11/1/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import SpriteKit

class NotchSpriteNode: SKSpriteNode {
    
    init() {
        super.init(texture: nil, color: UIColor.white, size: CGSize(width: 3, height: 20))
    }
    
    required init?(coder aDecoder: NSCoder) {
        super.init(texture: nil, color: UIColor.white, size: CGSize(width: 3, height: 20))
    }
    
    
}
